# BACKLOG — executable work orders

Statuses: `open` · `done` · `blocked: <reason>`. Agents: follow `AGENT_LOOP.md`.
Acceptance tests live in `tests/test_backlog_tasks.py` (skip-marked goalposts).

## local-ok (a local model can do these)

### T01 — Ground the assistant with retrieval · open
Goal: `llm/ollama_client.py` gains `build_query_grounding(query, k=5)` that
uses `rag/retrieve.search` to fetch top-k termbank rows for the user's query
and formats them like `build_grounding_block`, but with UNVERIFIED rows
clearly suffixed `(unverified -- needs native review)`. `generate()` gains an
optional `query_grounding: bool = True` that appends this block to the system
prompt. Constraints: verified-only `build_grounding_block` stays unchanged;
no new deps; retrieval import stays at module level (it is light).
Files: `llm/ollama_client.py`. Test: `test_t01_query_grounding`.

### T02 — Studio: remove a clip · open
Goal: `studio/corpus_store.py` gains `remove_clip(corpus_dir, filename)` that
deletes the WAV from `clips/` and its manifest row (no renumbering; sequence
numbers keep counting up so filenames never collide). Returns True if removed.
Then `studio/server.py` gains `POST /api/remove` (form field `file`) and the
UI table gets a remove link (plain fetch + refresh).
Files: `studio/corpus_store.py`, `studio/server.py`, `studio/static/index.html`.
Test: `test_t02_remove_clip` (covers the store function only).

### T03 — Number normalizer scaffold · open
Goal: new `app/normalize.py` with `number_to_jinghpaw(n, numerals)` where
`numerals` is a dict {int: str} built ONLY from termbank rows in domain
`numbers` with `verified == "true"` (helper `load_verified_numerals(path)`).
Known n → its verified word; unknown/unverified n → raise
`NotImplementedError` (honest gap, no guessing, no composition rules yet —
composition needs native-speaker data, see H01).
Files: `app/normalize.py`. Test: `test_t03_number_normalizer`.

### T04 — Studio: auto-convert m4a/mp3 uploads when ffmpeg exists · open
Goal: in `studio/server.py`, if an upload is not .wav and `shutil.which("ffmpeg")`,
convert to 16 kHz mono WAV in the temp dir before validation; if no ffmpeg,
return a clear error naming the manual command. No test (needs ffmpeg);
verify manually. Files: `studio/server.py`.

### T06 — MOS evaluation sheet generator · open
Goal: new `tools/mos_sheet.py`: `make_mos_rows(manifest_rows, seed=0)` returns
shuffled rows `{file, text, naturalness_1to5: "", intelligibility_1to5: "",
notes: ""}` for native-listener scoring; CLI writes `mos_sheet.csv` from a
corpus dir. Pure stdlib + csv. Files: `tools/mos_sheet.py`.
Test: `test_t06_mos_sheet`.

### T07 — Bilingual UI string structure · open
Goal: `app/app.py` moves user-facing strings into a `STRINGS = {"en": {...},
"kac": {...}}` dict where every `kac` value is `""` (empty = fall back to en).
A tiny `t(key)` helper picks kac when non-empty. NO Kachin text is written —
translations arrive from the college (H01 workflow). Files: `app/app.py`.
No test; ruff + verify compile check suffice.

## strong-model (wait for a frontier session)

### T08 — PWA service worker for web/ · open
Guaranteed first-visit-offline caching of app + model files; needs careful
cache versioning against HF CDN headers.

### T09 — Studio "Start fine-tune" button · open
Shells out to the RUNBOOK flow with progress streaming; only meaningful after
H02 corpus exists. Design the failure UX before building.

## human-only (no model attempts these)

- **H01 — Termbank native verification** (15 min, Dan + elder): review the 13
  seed rows; flip `verified` with reviewer noted; add numerals 6-1000 spoken
  forms when possible (unlocks T03 for real).
- **H02 — Voice corpus** (voice actor + studio): record per
  `sft/recording-kit/`, ingest through the studio to 60 min / 2+ speakers.
- **H03 — ONNX convert + upload** (15 min + bandwidth):
  `bash web/convert_to_onnx.sh` then upload to HF
  `DanSengAwng/mms-tts-kac-onnx`; the live web demo starts speaking Kachin.
- **H04 — Fine-tune run** (Colab T4): follow `sft/RUNBOOK.md` once H02 done.
- **H05 — Domain CNAME** for the Pages demo (or ask a frontier session).
- **H06 — Generate demo samples** (2 min): `python demo/generate_samples.py`,
  commit the three WAVs so the README's "hear it" is real.
