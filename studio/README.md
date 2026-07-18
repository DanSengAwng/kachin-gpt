# Fine-Tuning Studio

A local web app for the people preparing data to fine-tune the Kachin voice.
Drop in your voice actor's recordings, get each one validated, pair it with the
Kachin text it reads, watch the corpus grow toward the training target, and ask
a built-in assistant for guidance — then export a clean, training-ready dataset.

```
Voice actor's WAV  ─▶  validate (real check)  ─▶  + Kachin text  ─▶  corpus grows
      drop in            PASS / WARN / FAIL         you type it         dashboard
                                                                            │
   Assistant (local Ollama) answers questions        Export ─▶ train_manifest.txt
   using the TRUE corpus numbers, never guessed          for the sft/ pipeline
```

## Why it runs locally (not on a domain)

It does real work a browser can't: runs the audio validator, manages files, and
talks to your local Ollama model. More importantly, it handles **raw voice
recordings tied to signed consent** — personal data that should stay on the
contributor's own machine, not a public server. Local-first is the correct
privacy posture here, and it keeps the tool free and offline-capable.

## Run it

```bash
pip install -r studio/requirements.txt
python studio/server.py
# open http://localhost:8000
```

Optional: start Ollama (`ollama serve`) for the conversational assistant. Without
it, the studio still validates, tracks, and exports — the assistant just reports
the computed corpus status instead of chatting.

## What each piece does

| Endpoint | Purpose |
|---|---|
| `POST /api/validate` | Runs the real `check_recording.analyze_wav` on an uploaded clip |
| `POST /api/add` | Validates, then adds the clip + transcript to the corpus (rejects FAILs) |
| `GET /api/corpus` | Live dashboard numbers + a truthful next-step line |
| `POST /api/chat` | Assistant reply (local Ollama), always grounded in real corpus numbers |
| `POST /api/export` | Writes `corpus/train_manifest.txt` for the `sft/` pipeline |

## The corpus on disk

```
studio/corpus/          (gitignored — never committed)
    clips/spkNN_RNNN.wav
    manifest.csv         file, speaker_id, text, duration_s, verdict
    train_manifest.txt   clips/<file>|<text>   (written by Export)
```

## Honesty & guardrails baked in

- **Numbers are computed, never guessed.** The assistant is handed the true
  corpus status and told not to contradict it, so it can't hallucinate progress.
- **FAILs don't enter the corpus.** Clipped, too-short, or wrong-format clips are
  rejected at `/api/add` — bad data never reaches training.
- **Speaker IDs, not names.** The UI labels the field "never a real name,"
  matching the recording-kit privacy convention.

## Where the training target comes from

Defaults (in `corpus_store.py`): **60 minutes** of audio across **2+ speakers**
before the corpus is marked ready. Adjust `TARGET_MINUTES` / `TARGET_SPEAKERS`
to your trainer's needs.

