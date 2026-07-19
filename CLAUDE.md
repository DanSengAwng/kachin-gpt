# CLAUDE.md — project context for Claude Code sessions

## What this is
Kachin GPT: open-source text-to-speech for Kachin (Jingpho), ~1M speakers,
built on `facebook/mms-tts-kac` (Meta MMS). Mission: give the language a
digital voice, with the community in the loop.

## Commands
```bash
python verify_phase1.py --fast   # checks without model download
python verify_phase1.py          # full verification (downloads ~145 MB once)
pytest -q                        # fast tests (numpy only)
RUN_SLOW=1 pytest -q             # + real synthesis test
python app/app.py                # launch the Gradio UI
ruff check .                     # lint
```

## Map
- `app/kachin_tts.py` — TTS core. Public API: `speak()`, `save_wav()`,
  `chunk_text()`. Heavy imports stay lazy (inside functions) — never move
  torch/transformers to module level.
- `app/app.py` — Gradio UI. Keep it thin; no logic worth testing.
- `verify_phase1.py` — proves README claims. Update it when claims change.
- `tests/` — fast by default; model inference gated behind `RUN_SLOW=1`.
- `termbank/` — CSV vocabulary with `verified` flag (native speakers only
  may set `true`).
- `rag/`, `sft/` — design docs for Phases 2–3. Don't stub code there until
  the phase starts.

## Conventions
1. **Verify before claim.** Any capability stated in the README needs a
   check in `verify_phase1.py` or a test.
2. **Never fabricate Kachin.** New Kachin text enters via the termbank with
   `verified: false` and honest `notes`. Only native speakers verify.
3. **Honest status.** README status table must match reality — update it in
   the same commit that changes capability.
4. **Small claims, tested.** Prefer shipping less with proof over more
   without.

## Model facts
`facebook/mms-tts-kac` · VITS · 16 kHz · lang code `kac` · license
CC-BY-NC 4.0 (non-commercial — code is MIT separately).

## Read these first (agent handoff)

- `BLUEPRINT.md` -- system map, 8 invariants, decision log. Invariants are non-negotiable.
- `AGENT_LOOP.md` -- the work protocol for local/weaker models: one task, one test, one commit.
- `BACKLOG.md` -- specced tasks. Local-model-safe tasks are marked; acceptance tests already exist skip-marked in `tests/test_backlog_tasks.py`.

