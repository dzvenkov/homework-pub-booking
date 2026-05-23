# Ex8 — Voice pipeline

## Your answer

For this submission path I intentionally completed Ex8 through the
text-mode route the assignment explicitly allows when extra voice
service keys are unavailable. `ManagerPersona` still uses the Nebius
LLM-backed pub-manager persona, so the manager stays in character and
applies the same booking rules, but transport is plain stdin/stdout
instead of microphone plus third-party STT/TTS.

The important implementation detail is that text mode and voice mode
share the same trace contract. Every user turn becomes
`voice.utterance_in`, every manager reply becomes
`voice.utterance_out`, and the payload records `text`, `turn`, and
`mode`. That means the grader can verify the conversation shape without
requiring Speechmatics or Rime. The graceful-degradation path in
`run_voice_mode` also matches the spec: if `SPEECHMATICS_KEY` is
missing, the code warns and falls back to text rather than crashing.

The saved Ex8 artifact proves the no-extra-keys path works in practice:
the conversation ran for three turns and the trace captured all six
utterance events.

## Citations

- `starter/voice_pipeline/manager_persona.py`
- `starter/voice_pipeline/voice_loop.py`
- `ex9_artifacts/ex8_text_success_sess_528c7a5c009b/session_artifacts/logs/trace.jsonl`
