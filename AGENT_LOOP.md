# AGENT_LOOP — protocol for any coding agent on this repo

You are working on Kachin GPT. Your judgment is NOT the referee — the test
suite is. Follow this loop exactly.

## The loop

1. **Orient.** Read `BLUEPRINT.md` (contracts + invariants). Open `BACKLOG.md`
   and pick the topmost task tagged `local-ok` whose status is `open`
   (or the task a human assigned you). One task at a time.
2. **Read the spec.** The task lists goal, files, constraints, and its
   acceptance test in `tests/test_backlog_tasks.py` (marked skip).
3. **Unskip the task's test.** Remove its `@pytest.mark.skip` line only.
4. **Implement the smallest diff that could work.** Touch only the files the
   spec names. Match the surrounding code style. No new dependencies unless
   the spec grants them.
5. **Verify.** Run, from the repo root:
   ```bash
   ruff check .
   pytest -q
   python verify_phase1.py --fast
   ```
   All three must pass. Red? Fix the CODE, never the test, and go to 4.
6. **Commit.** One task per commit. Message: `T0X: <task title>`.
   Update the task's status to `done` in `BACKLOG.md` in the same commit.
7. **Repeat** from 1, or stop if instructed to do one task.

## Hard rules (violating these is failure, even with green tests)

- Never edit `BLUEPRINT.md` invariants or the decision log.
- Never write Kachin-language text. Not one word. Kachin comes from humans.
- Never set `verified: true` in the termbank.
- Never touch `studio/corpus/` contents or weaken `.gitignore` rules.
- Never delete, weaken, or add skip-marks to existing passing tests.
- Never move torch/transformers imports to module level.
- Never add a paid API, telemetry, or network calls beyond localhost Ollama
  and (in `web/` only) the HF Hub.

## When stuck

After 3 failed attempts on the same task: revert your changes, restore the
skip marker, set the task status to `blocked: <one-line reason>` in
`BACKLOG.md`, commit that, and stop. A blocked note is a good outcome; a
hacked-green test is not.

## Escalation ladder

- `local-ok` → you.
- `strong-model` → leave for a frontier-model session.
- `human-only` → never attempt; these need native speakers, GPUs, or accounts.
