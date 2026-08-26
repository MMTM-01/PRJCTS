#!/usr/bin/env python3
"""
Pulls recorded sales calls out of GoHighLevel into a local cache.

What it does, in order:
  Step 1: Pages through /conversations/search for the location to build the
          list of conversations. Prints the conversation count.
  Step 2: For each conversation, reads its messages and keeps the ones that
          are phone calls longer than --min-duration seconds (drops misdials
          and voicemail blips, which carry no discovery signal).
  Step 3: Fetches the transcription for each call. Reports how many calls
          came back without one -- if that number is high, call transcription
          is probably not enabled on the account and you need the audio path
          instead (see README, "If transcription is not enabled").
  Step 4: Fetches the contact record behind each call for its tags, source,
          and custom fields.
  Step 5: Writes cache/calls/<messageId>.json, one file per call.

The cache is resumable: calls already on disk are skipped, so an interrupted
run can just be restarted. Nothing in cache/ is ever committed -- it holds
real client conversations.

Usage:
  .venv/bin/python fetch_calls.py                  # full pull
  .venv/bin/python fetch_calls.py --max-calls 5    # quick smoke test
  .venv/bin/python fetch_calls.py --probe          # inspect API shapes only
"""

import argparse
import json
import os
import sys
import time
from collections import Counter
from pathlib import Path

import requests

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

API_BASE = "https://services.leadconnectorhq.com"
API_VERSION = "2021-04-15"        # standard v2 endpoints
TRANSCRIPT_VERSION = "v3"         # the transcription endpoint wants this
REQUEST_DELAY = 0.25              # ~4 req/s; GHL bursts at 100 per 10s
MAX_RETRIES = 4
PAGE_SIZE = 100

CACHE = Path("cache")
CALL_DIR = CACHE / "calls"

_last_request_time = [0.0]


def polite_wait():
    elapsed = time.monotonic() - _last_request_time[0]
    if elapsed < REQUEST_DELAY:
        time.sleep(REQUEST_DELAY - elapsed)
    _last_request_time[0] = time.monotonic()


class GHL:
    """Thin GoHighLevel v2 client: auth, throttling, retry, 404-tolerance."""

    def __init__(self, token, location_id):
        self.location_id = location_id
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        })

    def get(self, path, params=None, version=API_VERSION, tolerate=(404,)):
        url = f"{API_BASE}{path}"
        headers = {"Version": version}
        for attempt in range(MAX_RETRIES):
            polite_wait()
            try:
                r = self.session.get(url, params=params, headers=headers, timeout=30)
            except requests.RequestException as e:
                if attempt == MAX_RETRIES - 1:
                    raise
                print(f"    network error ({e}); retrying", file=sys.stderr)
                time.sleep(2 ** attempt)
                continue

            if r.status_code == 429:
                wait = float(r.headers.get("Retry-After", 2 ** attempt))
                print(f"    rate limited; waiting {wait:.0f}s", file=sys.stderr)
                time.sleep(wait)
                continue
            if r.status_code in tolerate:
                return None
            if r.status_code >= 500 and attempt < MAX_RETRIES - 1:
                time.sleep(2 ** attempt)
                continue
            if not r.ok:
                raise RuntimeError(
                    f"{r.status_code} on {path}: {r.text[:300]}"
                )
            return r.json()
        raise RuntimeError(f"gave up on {path} after {MAX_RETRIES} attempts")

    def conversations(self, limit=None):
        """Yield conversation dicts, paging with the documented cursor."""
        seen, cursor = 0, None
        while True:
            params = {"locationId": self.location_id, "limit": PAGE_SIZE}
            if cursor:
                params["startAfterDate"] = cursor
            page = self.get("/conversations/search", params=params)
            convos = (page or {}).get("conversations") or []
            if not convos:
                return
            for c in convos:
                yield c
                seen += 1
                if limit and seen >= limit:
                    return
            nxt = convos[-1].get("sort") or convos[-1].get("lastMessageDate")
            if not nxt or nxt == cursor:
                return
            cursor = nxt

    def messages(self, conversation_id):
        page = self.get(f"/conversations/{conversation_id}/messages")
        if not page:
            return []
        msgs = page.get("messages")
        # the endpoint has been seen returning {"messages": {"messages": [...]}}
        if isinstance(msgs, dict):
            msgs = msgs.get("messages")
        return msgs or []

    def transcription(self, message_id):
        return self.get(
            f"/conversations/locations/{self.location_id}"
            f"/messages/{message_id}/transcription",
            version=TRANSCRIPT_VERSION,
        )

    def contact(self, contact_id):
        payload = self.get(f"/contacts/{contact_id}")
        return (payload or {}).get("contact") or payload


def is_call(msg):
    kind = str(msg.get("messageType") or msg.get("type") or "")
    return "CALL" in kind.upper()


def call_duration(msg):
    for key in ("duration", "callDuration", "meta"):
        val = msg.get(key)
        if isinstance(val, dict):
            val = val.get("callDuration") or val.get("duration")
        if isinstance(val, (int, float)):
            return int(val)
        if isinstance(val, str) and val.isdigit():
            return int(val)
    return None


def probe(client):
    """Print raw shapes for the first conversation, without writing anything.

    The response shapes below are built from GoHighLevel's published docs but
    have not been run against this account, so field names for call duration
    and channel numbering may need a nudge. Run this first.
    """
    for convo in client.conversations(limit=1):
        print("--- conversation ---")
        print(json.dumps(convo, indent=2)[:1500])
        msgs = client.messages(convo.get("id"))
        print(f"\n--- {len(msgs)} messages, types seen ---")
        print(Counter(str(m.get("messageType") or m.get("type")) for m in msgs))
        for m in msgs:
            if is_call(m):
                print("\n--- first call message ---")
                print(json.dumps(m, indent=2)[:1500])
                t = client.transcription(m.get("id"))
                print("\n--- transcription ---")
                print(json.dumps(t, indent=2)[:1500] if t
                      else "NONE (transcription likely not enabled)")
                return
        print("\nNo call messages in this conversation.")
        return
    print("No conversations returned. Check GHL_LOCATION_ID and token scopes.")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--max-calls", type=int, help="stop after N calls (smoke test)")
    ap.add_argument("--max-conversations", type=int,
                    help="stop scanning after N conversations")
    ap.add_argument("--min-duration", type=int, default=90,
                    help="skip calls shorter than this many seconds (default 90)")
    ap.add_argument("--probe", action="store_true",
                    help="print raw API shapes for one conversation and exit")
    ap.add_argument("--refetch", action="store_true",
                    help="re-download calls already in the cache")
    args = ap.parse_args()

    token = os.environ.get("GHL_TOKEN")
    location = os.environ.get("GHL_LOCATION_ID")
    if not token or not location:
        sys.exit("Missing GHL_TOKEN / GHL_LOCATION_ID. Copy .env.example to .env.")

    client = GHL(token, location)

    if args.probe:
        probe(client)
        return

    CALL_DIR.mkdir(parents=True, exist_ok=True)
    contacts_cache = {}
    stats = Counter()
    kept = 0

    print("Step 1/5: scanning conversations...")
    for convo in client.conversations(limit=args.max_conversations):
        stats["conversations"] += 1
        if stats["conversations"] % 25 == 0:
            print(f"  {stats['conversations']} conversations, {kept} calls kept")

        for msg in client.messages(convo.get("id")):
            if not is_call(msg):
                continue
            stats["calls_seen"] += 1

            secs = call_duration(msg)
            if secs is not None and secs < args.min_duration:
                stats["too_short"] += 1
                continue

            mid = msg.get("id")
            dest = CALL_DIR / f"{mid}.json"
            if dest.exists() and not args.refetch:
                stats["cached"] += 1
                kept += 1
                continue

            transcript = client.transcription(mid)
            if not transcript:
                stats["no_transcript"] += 1
                continue

            cid = msg.get("contactId") or convo.get("contactId")
            if cid and cid not in contacts_cache:
                contacts_cache[cid] = client.contact(cid) or {}

            dest.write_text(json.dumps({
                "messageId": mid,
                "conversationId": convo.get("id"),
                "contactId": cid,
                "direction": msg.get("direction"),
                "dateAdded": msg.get("dateAdded"),
                "durationSeconds": secs,
                "transcript": transcript,
                "contact": contacts_cache.get(cid, {}),
            }, indent=2))
            kept += 1
            stats["fetched"] += 1

            if args.max_calls and kept >= args.max_calls:
                print(f"\nReached --max-calls {args.max_calls}.")
                report(stats, kept)
                return

    report(stats, kept)


def report(stats, kept):
    print(f"\nDone. {kept} calls in {CALL_DIR}/")
    for k in ("conversations", "calls_seen", "too_short", "no_transcript",
              "cached", "fetched"):
        print(f"  {k:<16} {stats[k]}")
    if stats["no_transcript"] and stats["no_transcript"] >= stats["fetched"]:
        print("\n!! Most calls had no transcription. Call transcription may be")
        print("   off for this account -- see README, 'If transcription is")
        print("   not enabled'.")


if __name__ == "__main__":
    main()
