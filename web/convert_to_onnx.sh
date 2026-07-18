#!/usr/bin/env bash
# Convert facebook/mms-tts-kac to ONNX for in-browser use with transformers.js.
#
# Run this ONCE on a machine with Python 3.10+ and ~2 GB free disk. It produces
# a folder you upload to your Hugging Face account; after that the browser app
# (web/index.html) loads the voice with no server.
#
#   bash web/convert_to_onnx.sh
#
# Output: ./mms-tts-kac-onnx/  (contains onnx/ weights + tokenizer files)
set -euo pipefail

MODEL_ID="facebook/mms-tts-kac"
OUT_DIR="mms-tts-kac-onnx"

echo "==> Creating a clean Python virtual environment"
python3 -m venv .venv-convert
# shellcheck disable=SC1091
source .venv-convert/bin/activate
pip install --upgrade pip >/dev/null

echo "==> Cloning the transformers.js conversion tooling"
if [ ! -d transformers.js ]; then
  git clone --depth 1 https://github.com/huggingface/transformers.js.git
fi
cd transformers.js
pip install -r scripts/requirements.txt >/dev/null

echo "==> Exporting $MODEL_ID to ONNX (task: text-to-waveform)"
# --quantize makes the model small (~40-70 MB) for fast in-browser loading.
# --skip_validation avoids a known false-negative check on VITS models.
python -m scripts.convert \
  --quantize \
  --model_id "$MODEL_ID" \
  --task text-to-waveform \
  --skip_validation

cd ..
echo "==> Collecting output into ./$OUT_DIR"
rm -rf "$OUT_DIR"
cp -r "transformers.js/models/$MODEL_ID" "$OUT_DIR"

echo ""
echo "DONE. ONNX model is in ./$OUT_DIR"
echo "Next: upload it to your Hugging Face account, then it works in the browser."
echo "  huggingface-cli login"
echo "  huggingface-cli upload DanSengAwng/mms-tts-kac-onnx ./$OUT_DIR"
echo ""
echo "If 'text-to-waveform' errors, install Optimum from the VITS branch and retry:"
echo "  pip install \"git+https://github.com/huggingface/optimum.git\""

