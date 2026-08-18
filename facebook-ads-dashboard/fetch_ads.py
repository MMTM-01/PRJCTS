#!/usr/bin/env python3
"""Pull every ad + its numbers from the Meta Marketing API and inject the
result into the dashboard template.

Usage (from inside facebook-ads-dashboard/):

    python3 fetch_ads.py                 # fetch live data, write data/, inject
    python3 fetch_ads.py --sample        # skip the API, use sample-data.json
    python3 fetch_ads.py --fetch-only    # fetch + write data/ads-data.json only
    python3 fetch_ads.py --inject-only   # re-inject existing data/ads-data.json

Credentials: the access token comes from the META_ACCESS_TOKEN environment
variable — never from a file in this repo. The ad account id (act_...) lives
in config.json (not a secret). See SETUP.md for how to get both.

Output: data/ads-data.json (versioned envelope) and data/dashboard.html
(the template with data baked in — this is the file that gets published as
the Claude Artifact). Everything under data/ is gitignored; the committed
index.html keeps its data block empty.

Privacy: this script fetches counts and metrics only. It never requests
lead responses, names, or emails, so no client PII ever touches this repo.
"""

import argparse
import base64
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    import requests
except ImportError:  # --sample / --inject-only work without requests
    requests = None

HERE = Path(__file__).resolve().parent

GRAPH = "https://graph.facebook.com"

AD_FIELDS = (
    "id,name,effective_status,created_time,"
    "adset{id,name,daily_budget,lifetime_budget},"
    "campaign{id,name,objective},"
    "creative{id,thumbnail_url,object_story_spec}"
)

INSIGHT_FIELDS = (
    "ad_id,spend,impressions,reach,frequency,inline_link_clicks,"
    "actions,cost_per_action_type,ctr,cpc"
)

# Ranges baked into the dashboard. Key -> Graph API date_preset.
RANGES = {"7d": "last_7d", "14d": "last_14d", "30d": "last_30d", "life": "maximum"}

# action_types that count as a lead, in preference order. "lead" is Meta's
# rolled-up total; the others are fallbacks when it's absent.
LEAD_ACTIONS = (
    "lead",
    "onsite_conversion.lead_grouped",
    "leadgen_grouped",
    "offsite_conversion.fb_pixel_lead",
)


def die(msg):
    sys.exit(f"fetch_ads.py: error: {msg}")


def load_config(path):
    with open(path) as f:
        cfg = json.load(f)
    return cfg


# ---------------------------------------------------------------- Graph API

class Graph:
    def __init__(self, token, version):
        self.token = token
        self.base = f"{GRAPH}/{version}"

    def get(self, path, **params):
        """GET with retry/backoff on rate limits and transient errors."""
        params["access_token"] = self.token
        url = f"{self.base}/{path.lstrip('/')}"
        for attempt in range(5):
            resp = requests.get(url, params=params, timeout=60)
            if resp.status_code < 400:
                return resp.json()
            try:
                err = resp.json().get("error", {})
            except ValueError:
                err = {}
            code = err.get("code")
            transient = resp.status_code >= 500 or code in (1, 2, 4, 17, 32, 613, 80000, 80004)
            if transient and attempt < 4:
                wait = 2 ** (attempt + 1)
                print(f"  transient error (code {code}), retrying in {wait}s...")
                time.sleep(wait)
                continue
            hint = ""
            if code == 190:
                hint = " — the access token is invalid or expired; see SETUP.md to generate a new one"
            elif code in (10, 200, 294):
                hint = " — the token is missing ads_read permission for this ad account; see SETUP.md"
            die(f"Graph API {resp.status_code} on /{path}: {err.get('message', resp.text[:200])}{hint}")

    def get_all(self, path, **params):
        """Follow pagination, return the concatenated data list."""
        out = []
        data = self.get(path, **params)
        while True:
            out.extend(data.get("data", []))
            after = data.get("paging", {}).get("cursors", {}).get("after")
            if not after or not data.get("paging", {}).get("next"):
                return out
            params["after"] = after
            data = self.get(path, **params)


# ------------------------------------------------------------- lead helpers

def leads_from_actions(actions):
    if not actions:
        return 0
    by_type = {a.get("action_type"): float(a.get("value", 0)) for a in actions}
    for t in LEAD_ACTIONS:
        if t in by_type:
            return int(by_type[t])
    return 0


def leadgen_form_id(creative):
    """Dig the instant-form id out of the creative spec, wherever it hides."""
    spec = (creative or {}).get("object_story_spec") or {}
    for key in ("link_data", "video_data", "template_data"):
        d = spec.get(key) or {}
        fid = d.get("lead_gen_form_id")
        if fid:
            return str(fid)
        cta = (d.get("call_to_action") or {}).get("value") or {}
        fid = cta.get("lead_gen_form_id")
        if fid:
            return str(fid)
    return None


def fetch_thumb(url, max_kb):
    """Download a creative thumbnail and return it as a data URI (or None).
    Meta CDN URLs expire and are blocked by the artifact's CSP, so the image
    must be embedded."""
    if not url:
        return None
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
    except Exception:
        return None
    if len(resp.content) > max_kb * 1024:
        return None
    mime = resp.headers.get("Content-Type", "image/jpeg").split(";")[0]
    return f"data:{mime};base64,{base64.b64encode(resp.content).decode()}"


# ------------------------------------------------------------------ fetch

def summarize(row):
    spend = float(row.get("spend", 0) or 0)
    imps = int(row.get("impressions", 0) or 0)
    reach = int(row.get("reach", 0) or 0)
    clicks = int(row.get("inline_link_clicks", 0) or 0)
    leads = leads_from_actions(row.get("actions"))
    return {
        "spend": round(spend, 2),
        "leads": leads,
        "impressions": imps,
        "reach": reach,
        "frequency": float(row.get("frequency", 0) or 0),
        "clicks": clicks,
        "cpl": round(spend / leads, 2) if leads else None,
        "ctr": round(clicks / imps * 100, 2) if imps else 0,
        "cpc": round(spend / clicks, 2) if clicks else None,
    }


def fetch_live(cfg, token):
    account = cfg["ad_account_id"]
    if not account:
        die("config.json has no ad_account_id — see SETUP.md step 4")
    if not account.startswith("act_"):
        account = "act_" + account
    act_no = account[len("act_"):]
    g = Graph(token, cfg.get("graph_api_version", "v23.0"))

    statuses = ["ACTIVE"]
    if cfg.get("include_paused", True):
        statuses += ["PAUSED", "ADSET_PAUSED", "CAMPAIGN_PAUSED", "WITH_ISSUES"]

    print(f"Fetching ads for {account} ...")
    info = g.get(account, fields="name,currency,timezone_name")
    ads_raw = g.get_all(f"{account}/ads", fields=AD_FIELDS,
                        effective_status=json.dumps(statuses), limit=100)
    print(f"  {len(ads_raw)} ads")

    # Account-level insights at ad granularity: one call per range + daily.
    by_range = {}
    for key, preset in RANGES.items():
        print(f"Fetching insights ({key}) ...")
        rows = g.get_all(f"{account}/insights", level="ad", date_preset=preset,
                         fields=INSIGHT_FIELDS, limit=200)
        by_range[key] = {r["ad_id"]: r for r in rows}

    print("Fetching daily series (last 30 days) ...")
    daily_rows = g.get_all(f"{account}/insights", level="ad",
                           date_preset="last_30d", time_increment=1,
                           fields="ad_id,date_start,spend,impressions,inline_link_clicks,actions",
                           limit=500)
    daily_by_ad = {}
    for r in daily_rows:
        daily_by_ad.setdefault(r["ad_id"], []).append({
            "d": r["date_start"],
            "spend": round(float(r.get("spend", 0) or 0), 2),
            "leads": leads_from_actions(r.get("actions")),
            "impressions": int(r.get("impressions", 0) or 0),
            "clicks": int(r.get("inline_link_clicks", 0) or 0),
        })

    empty = summarize({})
    ads = []
    for a in ads_raw:
        creative = a.get("creative") or {}
        form_id = leadgen_form_id(creative)
        print(f"  thumbnail: {a['name'][:50]}")
        thumb = fetch_thumb(creative.get("thumbnail_url"), cfg.get("max_thumb_kb", 45))
        ads.append({
            "id": a["id"],
            "name": a.get("name", a["id"]),
            "status": a.get("effective_status", "UNKNOWN"),
            "campaign": a.get("campaign") or {},
            "adset": {
                "id": (a.get("adset") or {}).get("id"),
                "name": (a.get("adset") or {}).get("name"),
                "daily_budget": (int((a.get("adset") or {}).get("daily_budget", 0) or 0) / 100) or None,
            },
            "created_time": (a.get("created_time") or "")[:10],
            "thumb": thumb,
            "lead_source": "instant_form" if form_id else "website",
            "leadgen_form_id": form_id,
            "links": {
                "ads_manager": f"https://adsmanager.facebook.com/adsmanager/manage/ads"
                               f"?act={act_no}&selected_ad_ids={a['id']}",
                "leads": (f"https://business.facebook.com/latest/leads_center"
                          f"?form_id={form_id}" if form_id else None),
            },
            "totals": {key: (summarize(by_range[key][a["id"]])
                             if a["id"] in by_range[key] else dict(empty))
                       for key in RANGES},
            "daily": sorted(daily_by_ad.get(a["id"], []), key=lambda x: x["d"]),
        })

    return {
        "v": 1,
        "sample": False,
        "fetched_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "account": {"id": account, "name": info.get("name"),
                    "currency": info.get("currency", cfg.get("currency", "USD")),
                    "timezone": info.get("timezone_name", cfg.get("timezone"))},
        "links": {
            "ads_manager": f"https://adsmanager.facebook.com/adsmanager/manage/ads?act={act_no}",
            "leads_center": "https://business.facebook.com/latest/leads_center",
            "gohighlevel": cfg.get("gohighlevel_url") or None,
        },
        "ads": ads,
    }


# ------------------------------------------------------------------ inject

DATA_BLOCK = re.compile(
    r'(<script id="adsdata" type="application/json">).*?(</script>)', re.S)


def inject(template_path, payload, out_path):
    html = Path(template_path).read_text()
    if not DATA_BLOCK.search(html):
        die(f'{template_path} has no <script id="adsdata"> block')
    blob = json.dumps(payload, separators=(",", ":")).replace("</", "<\\/")
    html = DATA_BLOCK.sub(lambda m: m.group(1) + blob + m.group(2), html, count=1)
    Path(out_path).write_text(html)
    print(f"Injected {len(blob) // 1024} KB of data -> {out_path}")


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--sample", action="store_true",
                   help="use sample-data.json instead of calling the API")
    p.add_argument("--fetch-only", action="store_true",
                   help="fetch and write data/ads-data.json, skip injection")
    p.add_argument("--inject-only", action="store_true",
                   help="re-inject existing data/ads-data.json, skip the API")
    p.add_argument("--config", default=HERE / "config.json")
    p.add_argument("--template", default=HERE / "index.html")
    p.add_argument("--out-dir", default=HERE / "data")
    args = p.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    data_file = out_dir / "ads-data.json"
    cfg = load_config(args.config)

    if args.sample:
        payload = json.loads((HERE / "sample-data.json").read_text())
        print("Using sample-data.json (no API calls)")
    elif args.inject_only:
        payload = json.loads(data_file.read_text())
        print(f"Re-injecting {data_file}")
    else:
        if requests is None:
            die("the 'requests' package is required for live fetches: pip install -r requirements.txt")
        token = os.environ.get("META_ACCESS_TOKEN")
        if not token:
            die("META_ACCESS_TOKEN is not set — see SETUP.md, or use --sample")
        payload = fetch_live(cfg, token)

    if not args.inject_only:
        data_file.write_text(json.dumps(payload, indent=1))
        print(f"Wrote {data_file}")

    if not args.fetch_only:
        inject(args.template, payload, out_dir / "dashboard.html")
        total = sum(a["totals"]["30d"]["spend"] for a in payload["ads"])
        leads = sum(a["totals"]["30d"]["leads"] for a in payload["ads"])
        print(f"{len(payload['ads'])} ads | last 30d: "
              f"${total:,.2f} spend, {leads} leads")


if __name__ == "__main__":
    main()
