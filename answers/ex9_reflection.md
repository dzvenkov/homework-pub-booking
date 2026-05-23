# Ex9 — Reflection

## Q1 — Planner handoff decision

### Your answer

In the Ex7 artifact I actually committed, the loop-side planner does
not assign a subgoal to `structured`; that is visible in the planner
ticket outputs, which keep the work on the loop half. The real handoff
signal appears one step later in the executor trace. At line 5 of the
saved `trace.jsonl`, the executor calls `handoff_to_structured` with
the reason `"loop half identified a candidate venue; passing to
structured half for confirmation under policy rules"`. That is the
moment the run crosses from open-ended search into rules-based
confirmation. The payload also includes `action="confirm_booking"`,
`party_size="12"`, and the chosen venue, so the signal is not generic;
it is specifically "we found a candidate, now apply policy."

This detail matters because the current Ex7 runner keeps the loop half
scripted even in `--real`, so the strongest evidence is not an
`assigned_half: "structured"` field in planner output. Instead, the
preserved logs show the executor-driven handoff plus the immediate
bridge transition from `loop` to `structured` at trace line 6. The
signal that caused the transition was the need for policy enforcement on
a concrete booking proposal, not more research.

### Citation

- `ex9_artifacts/ex7_real_success_sess_804d83ef21b7/session_artifacts/sess_804d83ef21b7/logs/trace.jsonl:5`
- `ex9_artifacts/ex7_real_success_sess_804d83ef21b7/session_artifacts/sess_804d83ef21b7/logs/trace.jsonl:6`
- `ex9_artifacts/ex7_real_success_sess_804d83ef21b7/session_artifacts/sess_804d83ef21b7/logs/tickets/tk_5240eb12/raw_output.json`

---

## Q2 — Dataflow integrity catch

### Your answer

I did not preserve a committed Ex5 session where `verify_dataflow`
actually fired, so the honest answer is the second branch of the
question: a specific scenario where it would catch something I might
miss by eye. In the saved Ex5 flyer, the final HTML contains concrete
facts such as venue name, weather, total cost, and deposit. A very
plausible failure is that the model rewrites only one of those values
while keeping the rest of the flyer coherent. For example, if the flyer
said `Deposit required: £300` instead of the tool-derived deposit, a
human reviewer could easily let it pass because `£300` sounds like a
reasonable pub-booking threshold.

That is exactly the kind of bug the integrity check is meant to catch.
`verify_dataflow` does not ask whether a number looks plausible; it asks
whether that exact fact appeared in a prior tool output recorded in
`_TOOL_CALL_LOG`. So a single edited amount, weather label, or venue
name should fail even if the rest of the page still looks polished. The
test case is easy to construct: run Ex5, edit one displayed fact in the
saved flyer by hand, then rerun the checker and expect a failed result.

### Citation

- `starter/edinburgh_research/integrity.py`
- `ex9_artifacts/ex5_real_success_sess_cdfdc70b3fcb/sess_cdfdc70b3fcb/workspace/flyer.html`
- `ex9_artifacts/ex5_real_success_sess_cdfdc70b3fcb/sess_cdfdc70b3fcb/logs/trace.jsonl:1`
- `ex9_artifacts/ex5_real_success_sess_cdfdc70b3fcb/sess_cdfdc70b3fcb/logs/trace.jsonl:2`

---

## Q3 — Removing one framework primitive

### Your answer

The first production failure I would expect is a partially-written
handoff file causing the structured half to read incomplete booking
data. The one primitive I would rely on to surface that is **IPC atomic
rename**. Ex7 is the clearest place to see why. In the saved session,
the bridge writes a concrete `handoff_to_structured.json`, then the
trace moves cleanly from `loop` to `structured`, later from
`structured` back to `loop`, and finally to `complete`. That clean
sequence assumes the consumer never observes a half-written handoff.

If I removed atomic rename and replaced it with naive "open file and
write in place," the structured half could read a truncated payload:
maybe the `confirm_booking` action is present but `party_size` or
`venue_id` is missing. The resulting failure would look random from the
LLM side, but the IPC primitive would surface it because the directory
would contain malformed or premature handoff state instead of a fully
materialised file. That is one concrete primitive and one concrete
failure mode: atomic rename protects the bridge from torn handoff
writes.

### Citation

- `ex9_artifacts/ex7_real_success_sess_804d83ef21b7/session_artifacts/sess_804d83ef21b7/ipc/handoff_to_structured.json`
- `ex9_artifacts/ex7_real_success_sess_804d83ef21b7/session_artifacts/sess_804d83ef21b7/logs/trace.jsonl:6`
- `ex9_artifacts/ex7_real_success_sess_804d83ef21b7/session_artifacts/sess_804d83ef21b7/logs/trace.jsonl:7`
