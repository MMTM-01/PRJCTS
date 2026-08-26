# PRJCTS — Momentum Fitness Product Workshop

This is the **staging repository** for new Momentum Fitness software.
Products are built, tested, and refined here; once a project is finalized
and proven in day-to-day use, it graduates into the
[`momentum-coo-os`](https://github.com/MMTM-01) repo.

Expect this repo to hold **many unrelated projects side by side**. Each one
lives in its own top-level folder and is fully self-contained — its own
README, its own dependencies, its own outputs. Nothing but repo-wide
housekeeping files belong at the root.

## Projects

| Project | What it is | Status |
|---|---|---|
| [`technical-seo-audit/`](technical-seo-audit/) | Python crawler that audits themomentumfitness.com — titles, meta, headings, schema, broken links, heavy media — plus the written audit report and fix playbook. | ✅ Audit complete (July 2026); rerun anytime |
| [`discovery-email-generator/`](discovery-email-generator/) | Single-page web app for turning Discovery Meeting intake into a branded follow-up email, with a shared client portal. Runs as a published Claude Artifact. | 🟢 In use at the front desk |
| [`sales-call-faq-analysis/`](sales-call-faq-analysis/) | Pulls recorded sales calls from GoHighLevel, extracts the questions prospects asked, and groups them by avatar/ICP segment. | 🟡 Scripts written, not yet run live |

## Repo layout

```
PRJCTS/
├── README.md                  ← you are here
├── CLAUDE.md                  ← conventions for Claude Code sessions
├── .gitignore
├── technical-seo-audit/
│   ├── README.md
│   ├── seo_audit.py
│   ├── requirements.txt
│   ├── schema-localbusiness.json
│   └── reports/               ← crawl data + written deliverables
└── discovery-email-generator/
    ├── README.md
    └── index.html
```

## Starting a new project

1. Create a top-level folder named in `kebab-case` (`client-intake-forms`,
   not `ClientIntake` or `new_project`).
2. Give it a `README.md` that answers, in plain language: what it does, who
   uses it, how to run it, and what state it's in.
3. Keep dependencies inside the project folder — `requirements.txt` for
   Python, `package.json` for Node. Never add a shared root-level
   dependency file.
4. Write generated output to a subfolder of the project (`reports/`,
   `output/`), never to the repo root.
5. Do a normal Claude Code session on a `claude/*` branch, then merge to
   `main` when it works.

## Graduating a project to `momentum-coo-os`

Before a project moves over, it should have:

- [ ] A README a non-technical staff member can follow without help
- [ ] No secrets, API keys, or real client data anywhere in its history
- [ ] Dependencies pinned in its own manifest
- [ ] Been used for real work at least once, with the rough edges fixed
- [ ] Any manual setup steps (env vars, accounts, plugin installs) written down

## House rules

- **Never commit secrets.** No API keys, passwords, or `.env` files. Use
  `.env` locally (it's gitignored) and document the required variable names
  in the project README.
- **Never commit real client data.** Client names, emails, and intake
  records stay out of git — see the warning in
  [`discovery-email-generator/README.md`](discovery-email-generator/README.md).
- Business contact info that's already public (the gym's address, phone,
  and info@ email) is fine to commit.
- `main` is the stable branch. Work happens on `claude/*` branches and gets
  merged in.
