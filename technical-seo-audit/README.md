# Momentum Fitness — Technical SEO Audit

Audit workspace for **https://themomentumfitness.com** (Momentum Proactive
Health & Fitness, Pantego TX — targeting Arlington and Mansfield searches).

## ✅ Current status: audit complete (July 18, 2026)

The crawl ran successfully against all **62 pages** in the sitemap.
**Read [`reports/audit-report.md`](reports/audit-report.md) for the plain-English top-10 findings and a
week-by-week fix plan.** The raw data is in `reports/audit-data.csv` (one row per
page, opens in Excel/Google Sheets) and `reports/audit-raw.json`.

Headline findings: a 27 MB autoplay homepage video, 38 pages with default
"- Momentum Fitness" titles, 12 near-empty orphaned trainer pages, junk
archive pages in the sitemap, and schema that claims the gym is open 9–5
seven days a week. Full details and fixes in the report.

## What's in this project

| File | What it is |
|---|---|
| `seo_audit.py` | The complete crawler. Reads robots.txt + sitemap, crawls every page at 1 request/second with a normal browser user-agent, extracts titles, meta descriptions, H1s, heading outlines, canonicals, meta robots, image alt text + junk filenames, JSON-LD schema, internal links (with 404 checks), word counts, video counts, and media file sizes. Then runs the sitewide analysis (duplicates, unoptimized "- Momentum Fitness" titles, redirect chains, orphan pages, 20 heaviest media files, schema summary). |
| `schema-localbusiness.json` | **Ready now.** Ready-to-paste LocalBusiness/HealthClub JSON-LD for the site (see below). |
| `requirements.txt` | Python dependencies (`requests`, `beautifulsoup4`). |
| `reports/` | Everything the July 18, 2026 crawl produced, plus the written deliverables. |

Inside `reports/`:

| File | What it is |
|---|---|
| `audit-report.md` | **Start here.** Plain-English top-10 findings ranked by impact, with a week-by-week fix plan. |
| `SEO-Fix-Playbook.md` | Paste-ready content and click-by-click paths for each fix. |
| `Momentum-Fitness-SEO-Audit.pdf` | PDF of the audit report, for sharing. |
| `Momentum-Fitness-SEO-Fix-Playbook.pdf` | PDF of the fix playbook, for sharing. |
| `audit-data.csv` | One row per page with every extracted field (opens in Excel/Google Sheets). |
| `audit-raw.json` | Full raw crawl data (heading outlines, per-image detail, schema blocks). |

The crawler regenerates `audit-data.csv` and `audit-raw.json`; the report,
playbook, and PDFs are written by hand from that data.

## How to run the crawl again

Run these from inside this `technical-seo-audit/` folder:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python seo_audit.py
```

It prints the total page count after Step 1 (sitemap discovery), then crawls.
A quick smoke test: `.venv/bin/python seo_audit.py --max-pages 3`

Results are written to `reports/`, **overwriting the July 2026 data files**.
To keep the existing ones for comparison, send the new run somewhere else:
`.venv/bin/python seo_audit.py --out-dir reports/2026-09`

## How to use `schema-localbusiness.json`

**Update after the crawl:** the site already outputs `ExerciseGym` +
`Organization` schema with correct address/geo/phone on ~50 pages (via the
SEO plugin), so pasting this file is now optional. The higher-priority fix
is correcting the opening hours in Rank Math → Local SEO — the live schema
currently claims 09:00–17:00 seven days a week (see [`reports/audit-report.md`](reports/audit-report.md),
item 9). Keep the file as a reference if you ever move off the plugin.

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
