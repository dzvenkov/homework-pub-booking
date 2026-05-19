## Ex5 Real Success Artifacts

Session id: `sess_cdfdc70b3fcb`

This folder preserves the successful `Ex5-real` run so it can be cited in `Ex9`.

### Key files

- Full copied session:
  [sess_cdfdc70b3fcb](D:\Homework\robspubs\homework-pub-booking\ex9_artifacts\ex5_real_success_sess_cdfdc70b3fcb\sess_cdfdc70b3fcb)
- Flyer:
  [flyer.html](D:\Homework\robspubs\homework-pub-booking\ex9_artifacts\ex5_real_success_sess_cdfdc70b3fcb\sess_cdfdc70b3fcb\workspace\flyer.html)
- Session state:
  [session.json](D:\Homework\robspubs\homework-pub-booking\ex9_artifacts\ex5_real_success_sess_cdfdc70b3fcb\sess_cdfdc70b3fcb\session.json)
- Trace:
  [trace.jsonl](D:\Homework\robspubs\homework-pub-booking\ex9_artifacts\ex5_real_success_sess_cdfdc70b3fcb\sess_cdfdc70b3fcb\logs\trace.jsonl)
- Planner ticket output:
  [raw_output.json](D:\Homework\robspubs\homework-pub-booking\ex9_artifacts\ex5_real_success_sess_cdfdc70b3fcb\sess_cdfdc70b3fcb\logs\tickets\tk_00d33870\raw_output.json)
- Narrated summary:
  [narrator.txt](D:\Homework\robspubs\homework-pub-booking\ex9_artifacts\ex5_real_success_sess_cdfdc70b3fcb\narrator.txt)

### Why this run matters

- It is the successful `Ex5-real` run after fixing the prompt flow so the planner saw the full task.
- The planner produced 2 bundled loop subgoals instead of losing critical state across many tiny subgoals.
- The run generated `workspace/flyer.html`.
- The dataflow integrity check passed.

### Useful talking points for Ex9

- Early real-mode failures came from the planner/executor losing constraints or state.
- Passing the full task prompt into `half.run(...)` improved planner fidelity.
- Adding a planning instruction to bundle dependent work made the successful run much more likely.
- The traces show real models can still be nondeterministic even when the local implementation is correct.
