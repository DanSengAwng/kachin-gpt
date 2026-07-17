# Architecture

```
┌─────────────┐      ┌──────────────────────┐      ┌────────────────────┐
│   Gradio UI │─────▶│   Language layer      │─────▶│  Voice engine       │
│  app/app.py │      │   Claude + termbank   │      │  facebook/mms-tts-  │
│ (audio out) │◀─────│   grounding (Phase 3) │◀─────│  kac → 16 kHz WAV   │
└─────────────┘      └──────────────────────┘      └────────────────────┘
                                                      app/kachin_tts.py
```

## Components

**Voice engine (`app/kachin_tts.py`) — Phase 1, verified.**
Wraps the MMS VITS checkpoint behind one public function, `speak()`. Heavy
imports are lazy so guards and pure functions are testable without the ML
stack. Long text is chunked on sentence boundaries and joined with short
pauses. Output is 16 kHz int16 PCM; `save_wav()` writes standard WAV files
with only the standard library.

**UI (`app/app.py`) — Phase 1.**
A minimal Gradio app: text in, audio out, seed examples. Deliberately thin —
it should never contain logic worth testing.

**Termbank (`termbank/`) — live schema, growing data.**
CSV with a `verified` flag that only native speakers may set. Consumed by
tests today, by retrieval in Phase 3.

**Grounded language layer (`rag/`) — designed.**
BM25 retrieval over the termbank pins curated terms into Claude's context;
uncovered requests degrade honestly. See `rag/README.md`.

**Fine-tuning harness (`sft/`) — designed.**
Data spec and pipeline for community-contributed recordings, evaluated by
native-listener MOS. See `sft/README.md`.

## Engineering principles

1. **Verify before claim.** `verify_phase1.py` checks everything the README
   asserts. Claims without checks don't ship.
2. **Lazy heavy imports.** The module imports with numpy alone; CI runs the
   fast test suite without torch.
3. **Swappable voice engine.** The model is one constant (`MODEL_ID`) and
   two private functions — replaceable when licensing or quality demands.
4. **Honest data model.** "Reviewed by a native speaker" is a column, not a
   hope.

