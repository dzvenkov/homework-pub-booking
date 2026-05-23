# Ex7 — Handoff bridge

## Your answer

Ex7 is the round-trip glue between the open-ended loop half and the
rule-bound structured half. The bridge keeps one current input payload,
runs the loop half, packages any forward handoff into a structured-half
request, and then either completes the session or builds a reverse task
when structured rejects. The reverse task is the important part: it
passes the previous loop result plus a human-readable rejection reason
back into the next loop turn, so the retry is informed instead of being
an unrelated fresh search.

The preserved Ex7 session shows the exact trajectory the assignment asks
for. Round 1 moves from loop to structured, then back to loop with
`party_too_large`. Round 2 hands off again with a revised proposal and
finishes in `complete`. That session also preserves the concrete
handoff payloads in executor tickets, which matters because Ex7 is not
just about state transitions in the abstract; it is about carrying full
context forward and the rejection reason backward without losing the
thread of the booking.

## Citations

- `starter/handoff_bridge/bridge.py`
- `ex9_artifacts/ex7_real_success_sess_804d83ef21b7/session_artifacts/sess_804d83ef21b7/logs/trace.jsonl`
- `ex9_artifacts/ex7_real_success_sess_804d83ef21b7/session_artifacts/sess_804d83ef21b7/logs/tickets/tk_5240eb12/raw_output.json`
- `ex9_artifacts/ex7_real_success_sess_804d83ef21b7/session_artifacts/sess_804d83ef21b7/logs/tickets/tk_a5549d37/raw_output.json`
