# Sales Call FAQ Analysis

Pulls recorded sales calls out of GoHighLevel, extracts the questions
prospects actually asked, and groups them by avatar/ICP segment so you can
see which worries belong to which kind of buyer.

Two scripts do the mechanical work; the clustering and avatar derivation are
done by reading the prepared bundle, because deciding that "what's the
damage?" and "how much per month?" are the same question is a judgment call,
not a regex.

## ⚠️ Where the data lives

**`MMTM-01/PRJCTS` is a public GitHub repository.** Call transcripts from a
gym contain names, phone numbers, emails, and health details — injuries,
surgeries, medications, weight. None of that belongs in a public repo, and
git history keeps it even after a delete.

So:

- `cache/` and `analysis/` are **gitignored**. They hold the real,
  fully-attributed data — that is the working set, and it stays on the
  machine that ran the scripts.
- `reports/` holds the written deliverable. Keep it aggregated. If a report
  needs to name individuals, it belongs in `cache/` too, not in git.
- Run `prep_analysis.py --anonymize` to produce a scrubbed bundle for
  anything that leaves the machine — a shared doc, an email, a contractor.

If the individual-level data genuinely needs to be committed and versioned,
make the repo private first, or put it in a private repo of its own. Ask
before changing this.

## Setup

```bash
cd sales-call-faq-analysis
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env      # then fill in the token and location id
```

The token is a **Private Integration Token** from GHL
(Settings → Private Integrations), with scopes `conversations.readonly`,
`conversations/message.readonly`, and `contacts.readonly`. The scripts use
their own credential rather than the Claude GHL connector, because pulling a
few hundred calls one API call at a time is a job for a script.

## Running it

```bash
# 1. Confirm the API shapes look as expected before pulling everything.
.venv/bin/python fetch_calls.py --probe

# 2. Smoke test, then the full pull. Resumable — rerun after an interruption.
.venv/bin/python fetch_calls.py --max-calls 5
.venv/bin/python fetch_calls.py

# 3. Build the analysis bundle.
.venv/bin/python prep_analysis.py
```

`fetch_calls.py` skips calls shorter than 90 seconds (`--min-duration`),
since misdials and voicemail blips carry no discovery signal.

`prep_analysis.py` writes three files into `analysis/`:

| File | What's in it |
|---|---|
| `questions.jsonl` | One record per question a prospect asked, tagged to the person, with a link to their GHL record |
| `profiles.jsonl` | Per call: the prospect's opening lines, duration, source, tags — the raw material for deriving avatars |
| `summary.txt` | Coverage counts and the channel-detection report |

## The channel problem

GoHighLevel labels each transcript segment with a `mediaChannel` but never
says which channel is the prospect and which is your rep. That matters a
lot: your rep asks far more questions than any prospect does, so mixing the
channels buries the real FAQs under your own discovery script.

`prep_analysis.py` scores each channel on rep-typical language ("thanks for
calling Momentum", "let me get you scheduled") and votes, **separately per
call direction** — the channels flip between inbound and outbound. Check the
detection report in `summary.txt` on the first run. If it looks wrong,
override it with `--prospect-channel N`.

## If transcription is not enabled

`fetch_calls.py` reports how many calls came back without a transcript. If
that number is most of them, call transcription is probably off for the
account. Two ways forward:

1. Turn it on in GHL and re-run — cleanest, and it backfills nothing, so it
   only helps calls from that point on.
2. Fall back to the audio: the recording endpoint
   (`GET /conversations/locations/{locationId}/messages/{messageId}/recording`)
   returns the file, and we transcribe it ourselves. Slower and costs
   compute, but it works on the entire back catalogue.

## Status

🟡 Scripts written, extraction logic tested against synthetic transcripts.
**Not yet run against the live account** — the API response shapes come from
GoHighLevel's published docs, so field names for call duration and channel
numbering may need a nudge on the first real run. That's what `--probe` is
for.
