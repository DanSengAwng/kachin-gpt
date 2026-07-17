# Kachin GPT 🔊

**Giving the Kachin language a digital voice.**

Kachin (Jingpho) is spoken by roughly **one million people** across Myanmar, China, India, and a global diaspora — and until now it has been almost entirely absent from the digital audio world. No voice assistant speaks it. No screen reader supports it. No navigation app can pronounce a Kachin place name.

Kachin GPT is an open-source text-to-speech system for Jinghpaw: **type a Kachin sentence, hear it spoken aloud in seconds.**

---

## Status: Phase 1 — Verified ✅

This project makes small claims and verifies them. Current state, honestly:

| Component | Path | Status |
|---|---|---|
| TTS core — `speak()` → 16 kHz PCM audio | `app/kachin_tts.py` | ✅ **Working & tested** |
| Gradio interface | `app/app.py` | ✅ **Working** |
| Phase 1 verification suite | `verify_phase1.py` | ✅ **Passing** |
| Terminology bank (names, places, domain vocab) | `termbank/` | 🚧 Live schema, growing data |
| Retrieval grounding for the language layer | `rag/` | 🗺️ Designed — Phase 3 |
| Fine-tuning harness for community recordings | `sft/` | 🗺️ Designed — Phase 2 |

What "verified" means here: the synthesis pipeline returns valid 16 kHz int16 audio, rejects empty input safely, and every claim in this table is checked by `verify_phase1.py` and the test suite. Nothing is claimed that the checks don't cover.

## Quickstart

```bash
git clone https://github.com/DanSengAwng/kachin-gpt
cd kachin-gpt
pip install -r requirements.txt
python app/app.py        # opens the web UI
```

First run downloads the Kachin voice model (~145 MB) from Hugging Face; after that it works fully offline. CPU is enough — no GPU required.

Or use it as a library:

```python
from app.kachin_tts import speak, save_wav

audio, sample_rate = speak("Chyeju kaba sai.")   # int16 waveform, 16 000 Hz
save_wav("Kaja ai i?", "hello.wav")
```

Verify everything yourself:

```bash
python verify_phase1.py          # full check (model download on first run)
pytest -q                        # fast tests, no ML stack needed
```

## How It Works

- **Voice engine:** [`facebook/mms-tts-kac`](https://huggingface.co/facebook/mms-tts-kac) from Meta's Massively Multilingual Speech project — one of the only neural models ever trained on Kachin (language code `kac`, of 1,100+ MMS languages). Kachin text is spoken directly; the language layer is for everything else.
- **Language layer (designed, Phase 3):** Claude drafts and explains Kachin text, grounded by a community-maintained terminology bank (`termbank/`) so proper nouns and domain vocabulary come from curated data — not model guesses. Low-resource languages are exactly where ungrounded LLM output fails; grounding is the design response.
- **Community loop (designed, Phase 2):** the `sft/` harness fine-tunes the voice on recordings contributed by native speakers, and quality is measured the honest way — Mean Opinion Score evaluations with native listeners.

## Why This Matters

Languages don't die dramatically. They die quietly — when the tools people live inside stop speaking them. Commercial voice AI will never prioritize a million speakers; the economics don't work. But open models plus one motivated builder genuinely can. This repo exists so that Kachin lives where its next generation of speakers actually lives: on their phones.

TTS for a low-resource language is also **accessibility infrastructure**: health information, legal notices, and education materials become audible to community members who speak Kachin fluently but read it less comfortably.

## Roadmap

- **Phase 1 — Verified synthesis** ✅ *(you are here)*
- **Phase 2 — Community fine-tuning:** native-speaker recordings → adapted voice → MOS evaluation
- **Phase 3 — Grounded language layer:** termbank retrieval + Claude, translate-and-speak, phrasebook mode
- **Phase 4 — Access:** hosted demo, stable API, dialect exploration

## Community & Ethics

- **Data provenance:** community recordings will be collected with informed consent; contributors choose attribution; data licensed for community benefit.
- **Community-in-the-loop:** native speakers verify termbank entries (the schema enforces it) and evaluate voice quality.
- **Not a replacement:** this is infrastructure for speakers and learners — a tool in service of the living language, not a substitute for it.

## Licensing — read this

- **Code:** MIT (`LICENSE`).
- **Voice model:** `facebook/mms-tts-kac` is **CC-BY-NC 4.0 — non-commercial**. This project is community infrastructure and complies; any commercial use would require a different voice model. The architecture keeps the voice engine swappable for exactly this reason.

## Built With Claude

This project is developed AI-first: planned, pair-built, and reviewed with **Claude Code**. The repo carries a `CLAUDE.md` so any Claude session loads full project context, and the workflow — scope → build → verify → document — is half the point: proof that one early-career builder plus Claude can ship infrastructure a language community actually needs.

## Contributing

The single most valuable contribution right now is **voice**: if you are a native Kachin speaker (or know one) willing to contribute recordings or review termbank entries, please open an issue. Code contributions welcome — start with `verify_phase1.py` to see the project's testing conventions.

---

*Phase 1 verified July 2026 · Every language deserves a digital voice.*
