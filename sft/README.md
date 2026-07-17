# Community Fine-Tuning Harness (design — Phase 2)

The base MMS model makes Kachin *speakable*; community fine-tuning makes it
*sound like home*. This directory holds the supervised fine-tuning (SFT)
pipeline for adapting the voice on recordings contributed by native
speakers.

## Data specification

| Property | Requirement |
|---|---|
| Format | 16 kHz, mono, WAV (matches model native rate) |
| Style | Script-read sentences, quiet room, consistent mic distance |
| Volume | 1–2 hours per speaker, 2–5 speakers to start |
| Transcripts | Sentence-aligned, Latin-script Jinghpaw, termbank-consistent spelling |
| Consent | Written informed consent; contributors choose attribution; data licensed for community benefit |

## Pipeline (planned)

1. **Collect** — recording scripts drawn from the termbank + everyday
   sentences; a simple guided checklist for contributors.
2. **Clean** — loudness normalization, silence trimming, noise screening;
   clips that fail automatic checks are rejected with feedback.
3. **Align** — transcript ↔ audio pairing, held-out validation split.
4. **Fine-tune** — adapt the VITS checkpoint (`facebook/mms-tts-kac`) on
   the community corpus; small learning rate, early stopping on held-out
   loss.
5. **Evaluate** — Mean Opinion Score (MOS) sessions with native listeners,
   base vs. fine-tuned, plus intelligibility transcription tests. Ship only
   if listeners prefer it.

## Why this is Phase 2, not Phase 1

Meaningful fine-tuning is gated on data that must be collected ethically and
with community trust — that is a partnership process, not a weekend task.
The harness is designed now so the first hour of contributed audio has
somewhere to go the day it arrives.

**Licensing note:** the base model is CC-BY-NC 4.0; fine-tuned derivatives
inherit non-commercial terms. See the repo README's licensing section.

