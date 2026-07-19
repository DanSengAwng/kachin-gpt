# Fine-Tuning Runbook -- MMS-TTS Kachin

**Status: written, not yet executed.** This is the pinned procedure for when the
corpus exists (target: 60 min across 2+ speakers -- see `studio/`). We do not
claim results we have not produced; this file becomes "verified" only after a
real run, with its numbers filled in at the bottom.

## What we are doing

Continue training `facebook/mms-tts-kac` (VITS) on community recordings so the
voice sounds like our speakers instead of the New Testament narrator. Framework:
[`ylacombe/finetune-hf-vits`](https://github.com/ylacombe/finetune-hf-vits) --
the standard recipe for MMS-TTS fine-tuning.

## Prerequisites (all produced by this repo)

| Input | Source | Gate |
|---|---|---|
| `corpus/clips/*.wav` 16 kHz mono | Studio dropzone (`studio/`) | every clip PASS from `check_recording.py` |
| `corpus/manifest.csv` | Studio auto-writes on add | text matches audio verbatim |
| `train.txt` (`clips/<file>|<text>`) | `POST /api/export` in Studio | -- |
| Consent forms signed | `sft/recording-kit/consent-form.md` | one per speaker, before training |

Hardware: free Colab T4 is enough (batch 8, fp16). Expect 2-4 h for ~60 min of audio.

## Procedure (Colab)

```bash
git clone https://github.com/ylacombe/finetune-hf-vits
cd finetune-hf-vits && pip install -r requirements.txt
# 1. Convert the discriminator checkpoint (one-time, per their README):
python convert_original_discriminator_checkpoint.py --language_code kac \
  --pytorch_dump_folder_path ./mms-kac-train
# 2. Build a HF dataset from our export: audio column = wav path,
#    text column = transcript, sampling_rate=16000.
# 3. Train:
accelerate launch run_vits_finetuning.py ./training_config.json
```

`training_config.json` starting point (tune only after a first honest run):

```json
{
  "model_name_or_path": "./mms-kac-train",
  "sampling_rate": 16000,
  "per_device_train_batch_size": 8,
  "learning_rate": 2e-5,
  "num_train_epochs": 200,
  "fp16": true,
  "weight_disc": 3, "weight_fmaps": 1, "weight_gen": 1,
  "weight_kl": 1.5, "weight_duration": 1, "weight_mel": 35
}
```

## Evaluation -- before any "it works" claim

1. Synthesize the 10-sentence held-out set (never trained on) with base AND tuned model.
2. Generate a blind MOS sheet (`tools/mos_sheet.py`, BACKLOG T06).
3. 2+ native listeners score naturalness + intelligibility, 1-5.
4. Tuned wins only if its mean MOS beats base. Publish both numbers either way.

## Integration

Tuned weights load through the existing code path -- change one string
(`app/kachin_tts.py: _MODEL_ID`) to the tuned checkpoint dir or HF repo.
License: derivative of CC-BY-NC 4.0 stays CC-BY-NC 4.0 (see BLUEPRINT invariant 6).

## Run log (filled after real runs -- do not pre-fill)

| Date | Corpus (min/speakers) | Steps | Base MOS | Tuned MOS | Verdict |
|---|---|---|---|---|---|
| -- | -- | -- | -- | -- | not yet run |
