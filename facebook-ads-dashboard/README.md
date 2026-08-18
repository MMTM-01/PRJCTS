# Momentum Fitness — Facebook Ads Dashboard ("Ad Pulse")

One page that shows every Facebook/Meta ad the gym is running with the
numbers that matter — spend, leads, cost per lead, reach, impressions,
frequency, daily trends — plus, per ad, a click that takes you to the form
responses that ad produced.

The dashboard is published as a **Claude Artifact** so it opens from any
device. It is **read-only**: numbers are pulled from the Meta Marketing API
by `fetch_ads.py` and baked into the page, then the page is republished.
(Unlike `discovery-email-generator`, republishing is always safe here — the
dashboard holds no user-entered data, so a redeploy can never wipe anything.)

## The pieces

| File | What it is |
|---|---|
| `index.html` | The dashboard template. Its `<script id="adsdata">` block is **empty in git** — data is injected into a copy, never committed. |
| `fetch_ads.py` | Pulls ads + insights from the Meta Graph API, writes `data/ads-data.json`, and injects it into `data/dashboard.html` (the file that gets published). |
| `sample-data.json` | Fake but realistic fixture — lets the dashboard run with zero credentials (`--sample`). |
| `config.json` | Non-secret settings: ad account id, GoHighLevel link, timezone. |
| `SETUP.md` | One-time Meta Business setup walkthrough (token + account id). |
| `data/` | All fetched output. **Gitignored** — nothing in it is ever committed. |

## Refreshing the dashboard

Tell a Claude Code session: **"refresh the ads dashboard"**. It runs:

```bash
cd facebook-ads-dashboard
pip install -r requirements.txt          # first time only
python3 fetch_ads.py                     # needs META_ACCESS_TOKEN (see SETUP.md)
```

…then republishes `data/dashboard.html` to the same artifact URL.

Useful variants:

```bash
python3 fetch_ads.py --sample        # no credentials; uses sample-data.json
python3 fetch_ads.py --fetch-only    # just write data/ads-data.json
python3 fetch_ads.py --inject-only   # re-inject the last fetch (template tweaks)
```

A daily auto-refresh (a scheduled Claude session doing the same steps each
morning) is planned once live credentials are in place.

## Where the "view leads" links go

- **Instant-form ads** (forms filled inside Facebook/Instagram): the ad's
  **Leads ⤓** button downloads that form's recent responses as a CSV from
  Meta (you must be logged into Facebook as a Page admin). The header's
  **Leads Center** link opens Meta's full leads inbox.
- **Website/funnel ads**: leads land in GoHighLevel, so the button opens the
  GHL app (URL configured in `config.json` → `gohighlevel_url`). Per-ad
  filtering inside GHL is possible later if UTM parameters are set up on the
  funnels — not built yet.
- **Ads Manager ↗** on every ad row jumps straight to that ad in Meta Ads
  Manager.

## Data & privacy rules (repo policy)

- The access token lives **only** in the `META_ACCESS_TOKEN` environment
  variable — never in a file in this repo.
- `fetch_ads.py` pulls **counts and metrics only** — it never requests lead
  names, emails, or responses, so no client PII can end up in git or in the
  published artifact.
- Everything under `data/` (fetched JSON + the injected dashboard build) is
  gitignored. The committed `index.html` keeps its data block empty.
