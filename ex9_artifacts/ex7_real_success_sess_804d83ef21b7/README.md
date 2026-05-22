# Ex7 Real Success Artifacts

This bundle preserves a successful persisted Ex7 run for Ex9.

Session:
- `sess_804d83ef21b7`

Outcome:
- completed
- rounds: 2

Why this run matters:
- It contains the full loop -> structured -> loop -> structured -> complete round-trip.
- The trace includes the bridge `session.state_changed` events needed for Ex9 Q1.
- The executor tickets show the exact `handoff_to_structured` payloads for both rounds.

Useful files:
- `terminal3-ex7-real.log` — top-level scenario output
- `session_artifacts/sess_804d83ef21b7/logs/trace.jsonl` — bridge state transitions
- `session_artifacts/sess_804d83ef21b7/logs/tickets/tk_5240eb12/raw_output.json` — round 1 handoff request
- `session_artifacts/sess_804d83ef21b7/logs/tickets/tk_a5549d37/raw_output.json` — round 2 handoff request
