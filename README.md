# Momentum Fitness — Technical SEO Audit

Audit workspace for **https://themomentumfitness.com** (Momentum Proactive
Health & Fitness, Pantego TX — targeting Arlington and Mansfield searches).

## ⚠️ Current status: crawl blocked by this workspace's network settings

Everything is built and tested, but **this cloud session was not allowed to
reach the public internet**, so the crawl itself could not run yet. This is
not a problem with your website — the site is live and healthy (verified via
web search). The sandbox that runs this code blocks outgoing web traffic
unless the environment is configured to allow it.

**How to fix (one-time, ~2 minutes):**

1. Go to [claude.ai/code](https://claude.ai/code) and open **Environments**
   (the settings for the environment this session runs in).
2. Set the environment's **Network access** policy to *Trusted* or *Full*
   network access (or add `themomentumfitness.com` to the allowed domains).
   Docs: https://code.claude.com/docs/en/claude-code-on-the-web
3. Start a new session on this repository and say:
   *"Run the SEO audit script and write up the report."*

## What's in this folder

| File | What it is |
|---|---|
| `seo_audit.py` | The complete crawler. Reads robots.txt + sitemap, crawls every page at 1 request/second with a normal browser user-agent, extracts titles, meta descriptions, H1s, heading outlines, canonicals, meta robots, image alt text + junk filenames, JSON-LD schema, internal links (with 404 checks), word counts, video counts, and media file sizes. Then runs the sitewide analysis (duplicates, unoptimized "- Momentum Fitness" titles, redirect chains, orphan pages, 20 heaviest media files, schema summary). |
| `schema-localbusiness.json` | **Ready now.** Ready-to-paste LocalBusiness/HealthClub JSON-LD for the site (see below). |
| `requirements.txt` | Python dependencies (`requests`, `beautifulsoup4`). |

When the crawl runs it produces:

- `audit-data.csv` — one row per page with every extracted field (opens in Excel/Google Sheets)
- `audit-raw.json` — full raw data (heading outlines, per-image detail, schema blocks)
- `audit-report.md` — plain-English top-10 problems ranked by impact (written after reviewing the crawl data)

## How to run the crawl (once network access is enabled)

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python seo_audit.py
```

It prints the total page count after Step 1 (sitemap discovery), then crawls.
A quick smoke test: `.venv/bin/python seo_audit.py --max-pages 3`

## How to use `schema-localbusiness.json`

This is the structured-data block that tells Google you're a local business
in Pantego serving Arlington and Mansfield. Before pasting:

1. Replace the `"image"` URL with a real photo/logo URL from your Media Library.
2. Fill in the `FILL_IN` opening hours (24-hour format, e.g. `"05:00"`,
   `"20:00"`). Delete the Saturday block if you're closed Saturdays.
3. Add more `sameAs` links if you have them (Instagram, Google Business
   Profile short link, Mindbody page, etc.).

**Where to paste it in WordPress/Elementor** (pick ONE):

- **Easiest:** install the free **WPCode** plugin → *Code Snippets → Header &
  Footer → Header* → paste the whole thing wrapped in
  `<script type="application/ld+json"> ... </script>` — this puts it on every
  page, which is what you want for LocalBusiness schema.
- **If you use Rank Math or Yoast SEO:** both have a "custom schema" /
  code-snippet feature under their Schema settings where the JSON can be
  pasted directly (no `<script>` wrapper needed in Rank Math's builder).
- **Elementor Pro:** *Site Settings → Custom Code → add to `<head>`*, wrapped
  in the same `<script type="application/ld+json">` tag.

After adding it, test the homepage at https://search.google.com/test/rich-results —
it should detect a "Local business" item with no errors.
