## Ex6 Real Success Artifacts

Session id: `sess_51d8b13ea788`

This folder preserves the successful manual tier-2 `Ex6-real` run so it can be cited in `Ex9`.

### Key files

- Full copied session:
  [sess_51d8b13ea788](D:\Homework\robspubs\homework-pub-booking\ex9_artifacts\ex6_real_success_sess_51d8b13ea788\sess_51d8b13ea788)
- Session state:
  [session.json](D:\Homework\robspubs\homework-pub-booking\ex9_artifacts\ex6_real_success_sess_51d8b13ea788\sess_51d8b13ea788\session.json)
- Manual run summary:
  [terminal_summary.txt](D:\Homework\robspubs\homework-pub-booking\ex9_artifacts\ex6_real_success_sess_51d8b13ea788\terminal_summary.txt)

### Why this run matters

- It confirms the real manual three-process Ex6 workflow succeeded:
  - `rasa-actions` on `:5055`
  - `rasa-serve` on `:5005`
  - `starter.rasa_half.run --real` posting to Rasa
- The structured half returned `complete`.
- The booking was confirmed with reference `BK-7D401E9E`.

### Notes for Ex9

- The Ex6 session directory is much sparser than Ex5 because this runner does not currently emit a `trace.jsonl`.
- The important evidence here is the successful manual tier-2 outcome plus the normalized booking payload and confirmation result captured in `terminal_summary.txt`.
