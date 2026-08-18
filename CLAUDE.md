# CLAUDE.md — working in this repo

Conventions for Claude Code sessions in `MMTM-01/PRJCTS`. Read this before
adding or moving files.

## What this repo is

A staging area for Momentum Fitness software. Multiple **unrelated**
projects live here side by side; finished ones graduate to
`momentum-coo-os`. Treat each top-level folder as an independent project
that happens to share a git remote.

## Structure rules

- **One folder per project, at the top level, in `kebab-case`.** Nothing
  project-specific goes at the repo root — no stray scripts, no shared
  `requirements.txt`, no project README at root.
- Root is reserved for `README.md`, `CLAUDE.md`, `.gitignore`, and any
  future repo-wide CI config.
- Every project folder has its own `README.md` and its own dependency
  manifest.
- Generated output goes in a subfolder of its project (`reports/`,
  `output/`) — never the repo root, and never another project's folder.
- Don't refactor across projects. A change to one project should not touch
  another's files.

## Current projects

### `technical-seo-audit/`
Python 3 + `requests` + `beautifulsoup4`. `seo_audit.py` crawls
themomentumfitness.com from its sitemap at 1 request/second and writes
`reports/audit-data.csv` and `reports/audit-raw.json`. Run it from inside
the project folder with a `.venv`; `--max-pages N` for a smoke test and
`--out-dir` to send results elsewhere.

The files in `reports/` are **real client deliverables** from the July 2026
crawl — the report, playbook, and PDFs were written by hand from the crawl
data. A rerun overwrites the CSV/JSON but not the written documents. Don't
regenerate or reword those documents unless asked.

### `discovery-email-generator/`
A single self-contained `index.html` — no build step, no dependencies. It
runs as a published Claude Artifact using the `artifact` capability
(self-republish, which is how the shared client roster persists) and
`downloads` (backup export).

**Critical:** the `<script id="db">` block holds the client database. In
this repo it is deliberately **empty**. The live artifact's copy holds real
client records, and republishing this file over it wipes them. Keep `#db`
empty in every commit, and flag the sync step whenever the user plans to
publish. See the project README for the full procedure.

## Data and secrets

- Never commit API keys, passwords, or `.env` files.
- Never commit real client data — names, emails, intake records.
- The gym's public contact details (address, phone, `info@` email) are fine;
  they're published in the site's structured data already.

## Git

- `main` is the stable branch. Do work on the `claude/*` branch assigned for
  the session and merge to `main` when it's working.
- Prefer `git mv` when relocating files so history follows them.
- Don't open a pull request unless the user asks for one.
