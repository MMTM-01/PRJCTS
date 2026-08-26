#!/usr/bin/env python3
"""
Turns the raw call cache into an analysis bundle.

What it does, in order:
  Step 1: Loads every cached call and flattens its transcript segments.
  Step 2: Works out which audio channel is the prospect and which is the
          sales rep. GoHighLevel tags each segment with a mediaChannel but
          does not say who is who, so this scores each channel on rep-typical
          language ("thanks for calling Momentum", "let me get you scheduled")
          and votes per call direction. Override with --prospect-channel if
          the detection report looks wrong.
  Step 3: Pulls question candidates from the prospect side only -- direct
          questions, and the indirect kind that carry the real objection
          ("I don't know if I'd be able to keep up").
  Step 4: Tags every question and profile to the person who said it -- name,
          contact id, and a direct link to their GHL record -- so findings
          stay traceable and you can verify or follow up on any single line.
          Pass --anonymize to scrub identities instead; use that for anything
          that leaves this machine.
  Step 5: Writes analysis/questions.jsonl, analysis/profiles.jsonl, and
          analysis/summary.txt.

cache/ and analysis/ are gitignored. They hold real client conversations and
MMTM-01/PRJCTS is a PUBLIC repository -- read README "Where the data lives"
before changing that.

Usage:
  .venv/bin/python prep_analysis.py                # attributed (default)
  .venv/bin/python prep_analysis.py --anonymize    # safe to share
  .venv/bin/python prep_analysis.py --prospect-channel 1
"""

import argparse
import json
import os
import re
from collections import Counter, defaultdict
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

CACHE = Path("cache/calls")
OUT = Path("analysis")
LOCATION_ID = os.environ.get("GHL_LOCATION_ID", "")

# Phrases a salesperson says and a prospect essentially never does.
REP_MARKERS = re.compile(
    r"(?i)\b(thanks? for calling|thank you for calling|how can i help"
    r"|momentum (proactive|fitness|health)|this is \w+ (with|at|from)"
    r"|let me (get|pull|check|look)|i can get you (in|scheduled|on)"
    r"|we (offer|have|do|provide)|our (trainers?|coaches?|program|team|facility)"
    r"|would you (like|be able) to come|does (that|monday|tuesday|wednesday"
    r"|thursday|friday|saturday|sunday) work|what i'?ll do is"
    r"|no problem at all|absolutely)\b"
)

# Direct questions, and the hedged statements that are really questions.
DIRECT_Q = re.compile(
    r"(?i)^\s*(what|when|where|why|who|how|which|do|does|did|can|could|will"
    r"|would|should|is|are|was|were|am|have|has|had|if i|any chance"
    r"|is there|are there)\b"
)
INDIRECT_Q = re.compile(
    r"(?i)\b(i (don'?t|do not) know if|i'?m not sure (if|how|whether|what)"
    r"|i was wondering|i'?d like to know|my (main )?(concern|worry|question)"
    r"|i'?m (worried|nervous|concerned|curious) about|what about"
    r"|the thing is|i just don'?t want to|as long as|i need to know"
    r"|i'?ve never|i'?m afraid)\b"
)

EMAIL = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.]+\b")
PHONE = re.compile(r"\b(?:\+?1[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b")
MONEY_KEEP = re.compile(r"\$\d")


def load_calls():
    for path in sorted(CACHE.glob("*.json")):
        try:
            yield json.loads(path.read_text())
        except json.JSONDecodeError:
            print(f"  skipping unreadable {path.name}")


def segments(call):
    """Normalize the transcription payload into (channel, start, text)."""
    raw = call.get("transcript")
    if isinstance(raw, dict):
        raw = (raw.get("transcriptions") or raw.get("transcript")
               or raw.get("data") or [])
    out = []
    for seg in raw or []:
        if not isinstance(seg, dict):
            continue
        text = (seg.get("transcript") or seg.get("text") or "").strip()
        if not text:
            continue
        out.append((
            seg.get("mediaChannel", seg.get("channel", 0)),
            seg.get("startTime", 0),
            text,
        ))
    out.sort(key=lambda s: s[1])
    return out


def detect_prospect_channel(calls):
    """Vote on which channel is the rep, separately per call direction."""
    votes = defaultdict(Counter)
    for call in calls:
        scores = Counter()
        channels = set()
        for chan, _, text in segments(call):
            channels.add(chan)
            scores[chan] += len(REP_MARKERS.findall(text))
        if len(channels) < 2:
            continue
        rep = scores.most_common(1)[0]
        if rep[1] == 0:
            continue
        others = channels - {rep[0]}
        votes[call.get("direction") or "unknown"][(rep[0], sorted(others)[0])] += 1

    mapping, report = {}, []
    for direction, tally in votes.items():
        (rep_chan, prospect_chan), n = tally.most_common(1)[0]
        total = sum(tally.values())
        mapping[direction] = prospect_chan
        report.append(
            f"  {direction:<10} prospect=channel {prospect_chan}, "
            f"rep=channel {rep_chan}  ({n}/{total} calls agree)"
        )
    return mapping, report


def scrub(text, contact, enabled=True):
    """Redact identity from a quote. A no-op unless --anonymize is set."""
    if not enabled:
        return text
    text = EMAIL.sub("[email]", text)
    text = PHONE.sub("[phone]", text)
    for key in ("firstName", "lastName", "name"):
        val = (contact or {}).get(key)
        if val and len(str(val)) > 2:
            for part in str(val).split():
                if len(part) > 2:
                    text = re.sub(rf"\b{re.escape(part)}\b", "[name]",
                                  text, flags=re.I)
    return text


def sentences(text):
    parts = re.split(r"(?<=[.?!])\s+", text)
    return [p.strip() for p in parts if p.strip()]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--prospect-channel", type=int,
                    help="force this channel as the prospect for every call")
    ap.add_argument("--profile-utterances", type=int, default=12,
                    help="prospect lines kept per call for avatar work (default 12)")
    ap.add_argument("--anonymize", action="store_true",
                    help="scrub names/phones/emails and drop identity fields; "
                         "use for any output that leaves this machine")
    args = ap.parse_args()

    if not CACHE.exists():
        raise SystemExit("No cache/calls/ -- run fetch_calls.py first.")

    calls = list(load_calls())
    if not calls:
        raise SystemExit("Cache is empty -- run fetch_calls.py first.")
    print(f"Step 1/5: loaded {len(calls)} calls")

    if args.prospect_channel is not None:
        mapping, report = {}, [f"  forced: prospect=channel {args.prospect_channel}"]
    else:
        mapping, report = detect_prospect_channel(calls)
    print("Step 2/5: channel detection")
    print("\n".join(report) or "  inconclusive -- pass --prospect-channel")

    OUT.mkdir(exist_ok=True)
    qf = (OUT / "questions.jsonl").open("w")
    pf = (OUT / "profiles.jsonl").open("w")
    stats = Counter()

    print("Step 3/5: extracting prospect questions")
    for call in calls:
        contact = call.get("contact") or {}
        direction = call.get("direction") or "unknown"
        want = (args.prospect_channel if args.prospect_channel is not None
                else mapping.get(direction))
        segs = segments(call)
        if not segs:
            stats["empty_transcript"] += 1
            continue
        if want is None:
            stats["channel_unknown"] += 1
            continue

        # Who said it. Kept on every record so a finding can be traced back
        # to one person and checked, unless --anonymize drops it.
        identity = {} if args.anonymize else {
            "contactId": call.get("contactId"),
            "contactName": " ".join(
                str(contact.get(k) or "") for k in ("firstName", "lastName")
            ).strip() or contact.get("name"),
            "email": contact.get("email"),
            "phone": contact.get("phone"),
            "callDate": call.get("dateAdded"),
            "crmLink": (
                f"https://app.gohighlevel.com/v2/location/{LOCATION_ID}"
                f"/contacts/detail/{call.get('contactId')}"
                if LOCATION_ID and call.get("contactId") else None
            ),
        }

        prospect = [t for chan, _, t in segs if chan == want]
        if not prospect:
            stats["no_prospect_audio"] += 1
            continue
        stats["analyzed"] += 1

        found = 0
        for line in prospect:
            for sent in sentences(line):
                if len(sent) < 8:
                    continue
                direct = sent.rstrip().endswith("?") or DIRECT_Q.match(sent)
                indirect = INDIRECT_Q.search(sent)
                if not (direct or indirect):
                    continue
                qf.write(json.dumps({
                    "callId": call.get("messageId"),
                    "kind": "direct" if direct else "indirect",
                    "text": scrub(sent, contact, args.anonymize),
                    **identity,
                }) + "\n")
                found += 1
        stats["questions"] += found
        if found == 0:
            stats["calls_without_questions"] += 1

        pf.write(json.dumps({
            "callId": call.get("messageId"),
            "direction": direction,
            "durationSeconds": call.get("durationSeconds"),
            "source": contact.get("source"),
            "tags": contact.get("tags") or [],
            "opening": [scrub(t, contact, args.anonymize)
                        for t in prospect[:args.profile_utterances]],
            **identity,
        }) + "\n")

    qf.close()
    pf.close()

    print("Step 4/5: " + ("identities scrubbed from all quotes" if args.anonymize
                          else "every quote tagged to the person who said it"))
    lines = [
        f"calls loaded            {len(calls)}",
        f"calls analyzed          {stats['analyzed']}",
        f"question candidates     {stats['questions']}",
        f"calls with no question  {stats['calls_without_questions']}",
        f"empty transcripts       {stats['empty_transcript']}",
        f"channel undetermined    {stats['channel_unknown']}",
        f"no prospect audio       {stats['no_prospect_audio']}",
        "",
        "channel detection:",
        *report,
    ]
    (OUT / "summary.txt").write_text("\n".join(lines) + "\n")
    print("Step 5/5: wrote analysis/questions.jsonl, profiles.jsonl, summary.txt\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
