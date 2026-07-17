# Roadmap

## Phase 1 — Verified synthesis ✅ (July 2026)
- [x] `speak()` returns valid 16 kHz int16 audio (verified)
- [x] Empty-input guard, sentence chunking, WAV export
- [x] Gradio interface with seed examples
- [x] Test suite + CI; termbank schema with review workflow

## Phase 2 — Community fine-tuning (next)
- [ ] Partner with 1–2 Kachin community organizations / diaspora groups
- [ ] Recruit 2–5 native speakers; collect 1–2 hrs clean recordings each
- [ ] Run the SFT pipeline (`sft/`); MOS evaluation with native listeners
- [ ] Publish fine-tuned weights (non-commercial, per base model license)

## Phase 3 — Grounded language layer
- [ ] BM25 retrieval over the termbank (`rag/`)
- [ ] Claude-drafted Kachin with pinned terminology + honest low-confidence UX
- [ ] Translate-and-speak mode (English → grounded Kachin → audio)
- [ ] Phrasebook mode: termbank entries with pre-generated audio

## Phase 4 — Access
- [ ] Hosted demo (Hugging Face Space)
- [ ] Stable API for third-party integration (education, accessibility)
- [ ] Dialect exploration (Rawang, Lisu-adjacent varieties) if data permits

## Success measures
- Native listeners rate fine-tuned voice ≥ base model on MOS
- ≥ 100 verified termbank entries reviewed by native speakers
- One community organization using the tool in real workflows

