# In-Browser Voice (Phase 4 preview)

The moonshot: the **entire Kachin voice model runs inside a phone's web
browser**. No server, no app install, no API cost — and after the first visit
it works **offline**. This is the difference between "come watch my laptop" and
"open this link on your phone right now."

```
Phone browser  ─loads once─▶  ONNX voice model (cached)  ─▶  speech, offline
   (index.html)                 mms-tts-kac, ~40-70 MB          no server ever
```

## What's here

| File | Purpose |
|---|---|
| `index.html` | The whole app — one self-contained page, hostable free on GitHub Pages |
| `convert_to_onnx.sh` | Run once locally to turn the Kachin model into browser-ready ONNX |

## Prove it works **today** (5 minutes, before converting anything)

The app can run the existing English MMS voice immediately, so you can confirm
the whole browser pipeline works before doing any conversion:

1. Open `index.html` — in `MODEL_ID`, switch `KACHIN_MODEL` to `ENGLISH_TEST`.
2. Open the page (locally, or once it's on GitHub Pages). Type "Hello", press
   the button. It downloads a small model and speaks — proving the pipeline.
3. Switch `MODEL_ID` back to the Kachin model for the real thing.

## Make the Kachin voice run in-browser (the real step)

No neural model of Kachin has ever run in a browser before — so there is no
ready-made ONNX build. You create it once:

1. **Convert** (one command, needs Python 3.10+ and ~2 GB disk):
   ```bash
   bash web/convert_to_onnx.sh
   ```
   This exports `facebook/mms-tts-kac` to quantized ONNX in `./mms-tts-kac-onnx/`.

2. **Upload** to your Hugging Face account (free):
   ```bash
   huggingface-cli login
   huggingface-cli upload DanSengAwng/mms-tts-kac-onnx ./mms-tts-kac-onnx
   ```
   You'd be publishing the first browser-ready Kachin voice model in existence.

3. **It just works.** `index.html` already points at
   `DanSengAwng/mms-tts-kac-onnx`. Open the page and press Speak.

## Host it free on GitHub Pages

1. On GitHub: **Settings ▸ Pages ▸ Build and deployment ▸ Source: Deploy from a
   branch**, branch `main`, folder `/ (root)`, Save.
2. After a minute your live link is:
   `https://dansengawng.github.io/kachin-gpt/web/`
3. Open it on a phone. Share the link. That is the demo.

## Offline & licensing notes

- **Offline:** transformers.js caches the model in the browser after first load,
  so repeat visits work with no connection. (A full PWA service-worker for
  guaranteed first-run-offline is a later polish.)
- **Licensing:** the MMS model is CC-BY-NC 4.0 (non-commercial). Community and
  educational use like this complies. Keep the model repo marked non-commercial.
- **Honesty:** this is verbatim synthesis — it reads exactly the text given.
  Quality is the base model's; Phase 2 fine-tuning (see `sft/`) improves it.

