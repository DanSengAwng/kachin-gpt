# BLUEPRINT — Master Architecture

The single source of truth for what Kachin GPT is, what is settled, and what
remains. **Any agent (human, local model, or frontier model) working on this
repo starts here**, then follows `AGENT_LOOP.md` against `BACKLOG.md`.

## Mission

Give the Kachin (Jinghpaw) language — ~1M speakers — a digital voice: verbatim
text-to-speech today, community-fine-tuned voice tomorrow, honest assistant
tooling around it. Community benefit, not commercial use.

## System map

| Component | Path | State | Contract |
|---|---|---|---|
| Voice engine | `app/kachin_tts.py` | ✅ verified | `speak(text, seed=None) -> (int16, 16000)`; warns on out-of-alphabet chars; raises on empty; NEVER calls an LLM |
| Gradio UI | `app/app.py` | ✅ working | thin; warm-up on start; no testable logic |
| Batch converter | `tools/speak_file.py` | ✅ working | text file(s) → WAV; paragraph pacing |
| Verification | `verify_phase1.py` | ✅ 14 checks | every README claim has a check |
| Tests + CI | `tests/`, `.github/workflows/ci.yml` | ✅ green | fast suite needs numpy only; model tests behind `RUN_SLOW=1` |
| Termbank | `termbank/termbank.csv` | ✅ schema live | `verified` flips true ONLY via native speaker |
| Retrieval | `rag/retrieve.py` | ✅ built | BM25 over termbank; verified rows boosted |
| Local assistant | `llm/ollama_client.py` | ✅ built | free/offline via Ollama; grounded on VERIFIED terms only; honesty rules in system prompt |
| Fine-tuning studio | `studio/` | ✅ built | local web app: validate → corpus → export manifest; corpus gitignored |
| Recording kit | `sft/recording-kit/` | ✅ built | session workflow, consent template, `check_recording.py` validator |
| SFT training | `sft/RUNBOOK.md` | 📋 spec | pinned runbook; needs GPU + corpus (human) |
| In-browser demo | `web/` | ✅ app live | transformers.js; awaits ONNX upload (human) to speak Kachin |
| ONNX conversion | `web/convert_to_onnx.sh` | 📋 script ready | run locally once; upload to HF `DanSengAwng/mms-tts-kac-onnx` |

Data flow (target state):

```
text ──▶ [normalize (T03)] ──▶ speak() ──▶ 16 kHz audio          (verbatim path)
user ──▶ retrieve (rag) ──▶ Ollama draft ──▶ NATIVE REVIEW ──▶ termbank/content
voice actor ──▶ studio validate ──▶ corpus ──▶ RUNBOOK fine-tune ──▶ better voice
```

## Invariants — never break these (tests enforce most)

1. **Verbatim mode is sacred.** The TTS path reads exactly the text given.
   No LLM ever touches it. This is the trust contract with the community.
2. **`verified: true` requires a native speaker.** No agent may flip it, add
   "obviously correct" Kachin, or ground the assistant on unverified rows.
3. **Never fabricate Kachin.** New Kachin text enters only as
   `verified: false` with honest notes, or from a human.
4. **Corpus stays local.** `studio/corpus/` is consent-gated voice data;
   gitignored; never uploaded anywhere by any task.
5. **Verify before claim.** New capability ⇒ test or verify_phase1 check in
   the same change. Never weaken a test to make it pass.
6. **Licensing.** Code MIT; `facebook/mms-tts-kac` is CC-BY-NC 4.0
   (non-commercial). Derivatives inherit NC. Keep the engine swappable.
7. **Lazy heavy imports.** torch/transformers only inside functions; the fast
   test suite must keep passing with numpy alone.
8. **Honest numbers.** Anything the assistant reports about corpus/progress is
   computed by code and pinned into the prompt, never model-estimated.

## Decision log (settled — do not re-litigate)

- **BM25 over embeddings** for termbank retrieval: corpus is tiny and
  keyword-shaped; transparent, dependency-free. Revisit only past ~2k rows.
- **Local-first studio, no hosted backend**: privacy of voice data + zero
  cost + offline. The public domain is reserved for the `web/` demo only.
- **Ollama for the assistant**: free, offline, model-agnostic
  (`OLLAMA_MODEL`). Claude/other APIs may be added as optional backends, never
  required.
- **Skipped-test goalposts**: unfinished tasks ship acceptance tests marked
  skip in `tests/test_backlog_tasks.py`; implementing = unskip + make green.
- **Web demo = static GitHub Pages + transformers.js**: no server ever;
  offline after first load; model lives on HF Hub.
- **"Kachin GPT" repo name, "verbatim by design" product framing** for
  community/theological audiences.

## Dependency graph for what remains

```
H01 termbank verification (human) ──▶ T03 numerals data ──▶ number reading
H02 voice corpus (human) ──▶ studio corpus ──▶ H04 RUNBOOK fine-tune ──▶ v2 voice
H03 ONNX upload (human, 15 min) ──▶ web demo speaks Kachin ──▶ H05 domain CNAME
T01 retrieval→assistant wiring (local-ok, test ready)
T02/T04/T06/T07 studio & tooling polish (local-ok)
T08 PWA offline, T09 train button (strong-model, after H02)
```

## Roles

- **Human (Dan / community):** everything tagged H; native review; recordings.
- **Local model via AGENT_LOOP.md:** tasks tagged `local-ok` in BACKLOG.md.
- **Frontier model (when available):** `strong-model` tasks; blueprint changes;
  new invariants. A frontier agent should re-read this file and update it —
  it is the only file allowed to change the rules, and only with rationale
  added to the decision log.
