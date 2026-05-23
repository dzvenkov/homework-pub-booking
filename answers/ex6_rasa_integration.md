# Ex6 — Rasa structured half

## Your answer

Ex6 is the structured-half side of the booking flow. The Python bridge
normalises a loose booking dict into a Rasa REST payload, sends it to
`/webhooks/rest/webhook`, and converts the reply back into a
`HalfResult`. The key requirement from the assignment is that
normalisation happens before the HTTP call, so Rasa receives consistent
types instead of free-form strings. My validator covers the fields the
spec calls out: it canonicalises `venue_id`, parses the date into
`YYYY-MM-DD`, converts party size into an integer, normalises times into
`HH:MM`, and converts deposits like `£200` into `deposit_gbp=200`.

The saved real Ex6 run shows the bridge working against live Rasa
services instead of the mock path. The final output for
`sess_b7affa8b0cee` contains a committed booking with canonical values:
`venue_id='haymarket_tap'`, `date='2026-04-25'`, `time='19:30'`,
`party_size=6`, and `deposit_gbp=200`. That is the core Ex6 behavior:
Rasa decides under explicit policy rules, but it receives clean,
deterministic input from the Python side first.

## Citations

- `starter/rasa_half/validator.py`
- `starter/rasa_half/structured_half.py`
- `ex9_artifacts/ex6-real-20260522-200138/terminal3-ex6-real.log`
