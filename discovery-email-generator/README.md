# Momentum Fitness — Discovery Email Generator

A single-page web app the front desk uses to turn a Discovery Meeting
intake form into a polished follow-up email, and to keep a shared record of
every client visit.

`index.html` is the whole application — no build step, no server, no
dependencies. It runs as a published **Claude Artifact**, which is how the
whole team reaches the same shared client roster.

## What it does

- **Email Builder** — fill in the Discovery Meeting details, then generate
  the follow-up email in either a **Classic Template** or a
  **Momentum Branded** layout. *Copy Subject* and *Copy Email* put the
  result on the clipboard, ready to paste into Gmail.
- **Client Portal** — *Save to Portal* writes the visit to a shared roster
  every team member sees. Clients are searchable; repeat visits stack under
  the same client via *Save as New Visit*.
- **Draft protection** — an in-progress form is mirrored to `localStorage`,
  so an unsaved draft survives a refresh or another staff member picking up
  the same front-desk device.
- **Export Backup** — downloads the full client database as a JSON file.

## ⚠️ Before you republish this file

**The live artifact holds the team's real client data. This repo copy does
not.**

The client database lives in the `<script id="db">` block near the top of
`index.html`. In this repository that block is intentionally **empty**
(`{"v":1,"clients":[]}`) so no client data is ever committed to git. The
published artifact rewrites its own `#db` block as staff save visits.

So: **publishing this file over the live artifact wipes the roster back to
empty.** If you need to ship a code change to the live app:

1. Open the live artifact and use **Export Backup** to save the current
   database.
2. Make your code change here.
3. Copy the live `#db` JSON into your copy before publishing — or publish,
   then restore from the backup file.
4. Never commit a `#db` block containing real client names or emails.

## How it stores data

The app asks for two Artifact runtime capabilities:

- `artifact` — lets the page rewrite and republish itself, which is how a
  saved visit becomes visible to everyone else.
- `downloads` — powers *Export Backup*.

If neither is available (for example, opening `index.html` straight from
disk), the app degrades to a `localStorage`-only mirror: the builder and
templates work fully, but saves stay on that one device.

## Local editing

Open `index.html` in any browser to work on the layout and templates. The
CSS lives in `<style id="appcss">` and the UI is rendered from JS template
strings further down the file. Test a change locally, then follow the
republish steps above to push it to the live artifact.
