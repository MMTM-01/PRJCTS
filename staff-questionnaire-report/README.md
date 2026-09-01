# Staff Questionnaire Report

Analysis of the Momentum Staff Questionnaire (the "Momentum Staff Questionnaire"
Claude Artifact, questionnaire v1). All 9 staff responses collected Aug 19–29,
2026 — CEO, manager (three hats), front desk, and six trainers.

## Contents

- `report.html` — the full report: findings, donut charts, efficiencies vs.
  deficiencies, what can/can't/shouldn't change, a 90-day implementation
  sequence, and a ranked list of apps to build. Published as the
  **"Momentum Staff Voices"** artifact:
  https://claude.ai/code/artifact/f2950963-85fb-4902-97d6-b377b14120fa
- `data/responses.json` — the raw response database extracted from the
  questionnaire artifact's `#db` block on Sep 1, 2026 (9 submissions).
- `data/questions.json` — the question definitions (`QUESTION_SETS`) extracted
  from the same artifact, keyed by role track. Question ids are stable; answers
  are keyed by these ids.

## Notes

- Responses are internal staff feedback — candid by design. Keep this folder
  out of anything member- or public-facing.
- `report.html` is self-contained (no build step). To update the published
  artifact, republish this file to the artifact URL above.
- If more responses come in later, re-extract the `#db` block from the
  questionnaire artifact and refresh `data/responses.json` before revising
  the report.
