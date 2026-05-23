# Ex5 — Edinburgh research loop scenario

## Your answer

Ex5 is the loop-half research scenario from the assignment: four
session-scoped tools gather venue, weather, and pricing facts, and the
scenario finishes by writing a flyer plus running a dataflow integrity
check. In my implementation, `venue_search`, `get_weather`, and
`calculate_cost` are read-only fixture lookups, while
`generate_flyer` is the only write step because it creates the final
artifact in the session workspace. The important contract is that every
tool call records its arguments and outputs into `_TOOL_CALL_LOG`, so
the flyer can be audited after generation instead of trusted blindly.

The preserved real-mode Ex5 bundle also shows the planning shape that
ended up working best: the planner produced two bundled subgoals rather
than many tiny ones, which kept dependent facts together long enough for
the loop half to finish the run. That matches the assignment's goal for
Ex5: open-ended research is still allowed, but the final flyer has to be
grounded in auditable tool outputs rather than free-form model prose.

## Citations

- `starter/edinburgh_research/tools.py`
- `starter/edinburgh_research/integrity.py`
- `starter/edinburgh_research/run.py`
- `ex9_artifacts/ex5_real_success_sess_cdfdc70b3fcb/sess_cdfdc70b3fcb/logs/trace.jsonl`
- `ex9_artifacts/ex5_real_success_sess_cdfdc70b3fcb/sess_cdfdc70b3fcb/workspace/flyer.html`
