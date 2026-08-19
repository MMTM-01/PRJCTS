# Momentum Fitness — Staff Discovery Questionnaire

A single-page web app that interviews the Momentum team — **trainers**,
**front desk**, the **CEO**, and **Josie** (who gets her own questionnaire
covering her trainer / admin / social-content hats). Each role gets
questions tailored to their seat, written from the COO's discovery
interview (see [`context/coo-interview.md`](context/coo-interview.md)).

`index.html` is the whole application — no build step, no server, no
dependencies. It runs as a published **Claude Artifact**; everyone answers
on the front-desk computer via the artifact link, and submissions land in
one shared store the COO reviews.

## How it works for staff

1. Open the artifact link, tap your role card.
2. Answer at your own pace — every keystroke is saved as a draft, so a
   refresh (or someone else using the computer) never loses work. An
   unfinished questionnaire shows up on the start screen with
   **Resume / Discard**.
3. Name is optional. Every question is skippable.
4. **Submit Answers** → confirm → done. The form clears for the next person.

Rough time per role: Front Desk ~10 min · Trainer 15–20 min ·
Josie 20–25 min · CEO 45–60 min.

## How it works for the COO

- Tap **COO review** at the bottom of the start screen. The PIN is **0817**.
  This is a courtesy screen, not security — anyone technical can read the
  page source, which contains all responses. It only keeps casual eyes off
  other people's answers.
- The review view lists every response grouped by role; expand one to read
  answers under their section headings. Deleting a response removes it for
  everyone (export a backup first).
- **Export JSON** — full backup of the response store.
- **Export CSV** — one row per answer (`responseId, role, name,
  submittedAt, section, questionId, question, answer`), opens in Excel or
  Google Sheets.
- **Import** — merge a JSON backup back in (dedupes by response id).

## ⚠️ Before you republish this file

**The live artifact holds the team's real answers. This repo copy does
not.**

Responses live in the `<script id="db">` block near the top of
`index.html`. In this repository that block is intentionally **empty**
(`{"v":1,"responses":[]}`) so no staff answers are ever committed to git.
The published artifact rewrites its own `#db` block as people submit.

So: **publishing this file over the live artifact wipes every submitted
response.** To ship a code change to the live app:

1. Open the live artifact's review view and **Export JSON**.
2. Make your code change here.
3. Copy the live `#db` JSON into your copy before publishing — or publish,
   then restore from the backup via **Import**.
4. Never commit a `#db` block containing real answers or names.

## Editing the questions

The question sets live in `QUESTION_SETS` inside `index.html`, one entry
per role (`trainer`, `josie`, `frontdesk`, `ceo`), each a list of sections
containing questions of type `text`, `rating` (1–5 with end labels), or
`choice` (tap-to-pick options).

Rules, because submitted answers are keyed by question id forever:

- **Question ids are stable.** Rewording a question keeps its id. Never
  reuse an old id for a new question.
- Adding or removing questions → bump `QUESTIONS_VERSION`.
- The review view falls back to showing the raw id for answers whose
  question was later removed, so old responses always stay readable.

## How it stores data

The app asks for two Artifact runtime capabilities:

- `artifact` — lets the page rewrite and republish itself, which is how a
  submission becomes visible to the COO from any device.
- `downloads` — powers the JSON/CSV exports.

If neither is available (for example, opening `index.html` straight from
disk), the app degrades to a `localStorage`-only mirror: the questionnaire
works fully, but submissions stay on that one device and the banner says
so.

## Publishing checklist (first launch)

1. Publish `index.html` as a Claude Artifact; grant the `artifact` and
   `downloads` capabilities when prompted.
2. Submit a test response from the front-desk computer, then open the
   artifact on a second device and confirm it appears in the review view.
3. Delete the test response, export a baseline JSON backup.
4. Bookmark the link on the front-desk computer and tell the team.

## Status

🟢 Built and locally verified (draft protection, submit flow, PIN review,
JSON/CSV export, self-republish round-trip). Awaiting first publish as an
artifact and real responses.
