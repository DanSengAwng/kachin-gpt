#!/usr/bin/env python3
"""Generate the demo audio samples listed in demo/samples/README.md.

Run from the repo root (downloads the model on first run):

    python demo/generate_samples.py
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from app.kachin_tts import save_wav  # noqa: E402

SAMPLES = {
    "chyeju_kaba_sai.wav": "Chyeju kaba sai.",
    "kaja_ai_i.wav": "Kaja ai i?",
    "numbers_1_to_5.wav": "Langai. Lahkawng. Masum. Mali. Manga.",
}


def main() -> None:
    out_dir = REPO_ROOT / "demo" / "samples"
    for filename, text in SAMPLES.items():
        path = save_wav(text, out_dir / filename)
        print(f"wrote {path}")
    print(f"\n{len(SAMPLES)} samples generated in {out_dir}")


if __name__ == "__main__":
    main()

