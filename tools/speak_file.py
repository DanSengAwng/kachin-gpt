#!/usr/bin/env python3
"""Batch text-to-audio: turn Kachin text files into WAV audio.

The tool for lessons, bulletins, and announcements -- write the text,
get audio you can share on a phone.

Usage (from the repo root):

    python tools/speak_file.py lesson.txt                 # -> lesson.wav
    python tools/speak_file.py a.txt b.txt c.txt          # batch mode
    python tools/speak_file.py lesson.txt -o out.wav      # explicit output
    python tools/speak_file.py lesson.txt --seed 42       # reproducible audio

Paragraphs (blank-line separated) are joined with a longer pause than
sentences, so chapter-length text keeps a natural reading rhythm.
To get MP3 for messaging apps, convert the WAV afterwards, e.g.:

    ffmpeg -i lesson.wav -b:a 64k lesson.mp3
"""

from __future__ import annotations

import argparse
import sys
import wave
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from app.kachin_tts import SAMPLE_RATE, check_text, speak  # noqa: E402

# Silence between paragraphs (seconds).
_PARAGRAPH_PAUSE_S = 0.6


def split_paragraphs(text: str) -> list[str]:
    """Split text into paragraphs on blank lines. Pure function."""
    paragraphs = [p.strip() for p in text.split("\n\n")]
    return [p for p in paragraphs if p]


def synthesize_file(in_path: Path, out_path: Path, seed: int | None) -> float:
    """Synthesize one text file to WAV. Returns audio duration in seconds."""
    text = in_path.read_text(encoding="utf-8")
    paragraphs = split_paragraphs(text)
    if not paragraphs:
        raise ValueError(f"{in_path}: file contains no text.")

    missing = check_text(text)
    if missing:
        print(f"  warning: characters outside the voice alphabet: {missing}")

    pause = np.zeros(int(_PARAGRAPH_PAUSE_S * SAMPLE_RATE), dtype=np.int16)
    parts: list[np.ndarray] = []
    for i, paragraph in enumerate(paragraphs):
        if i > 0:
            parts.append(pause)
        audio, _ = speak(paragraph, seed=seed)
        parts.append(audio)

    full_audio = np.concatenate(parts)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(out_path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(SAMPLE_RATE)
        wav_file.writeframes(full_audio.tobytes())
    return len(full_audio) / SAMPLE_RATE


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert Kachin text files to spoken WAV audio."
    )
    parser.add_argument("inputs", nargs="+", type=Path, help="UTF-8 text file(s)")
    parser.add_argument(
        "-o", "--output", type=Path, default=None,
        help="output WAV path (single input only; default: alongside input)",
    )
    parser.add_argument(
        "--seed", type=int, default=None,
        help="random seed for reproducible audio",
    )
    args = parser.parse_args()

    if args.output and len(args.inputs) > 1:
        parser.error("-o/--output only works with a single input file")

    failures = 0
    for in_path in args.inputs:
        out_path = args.output or in_path.with_suffix(".wav")
        print(f"{in_path} -> {out_path}")
        try:
            duration = synthesize_file(in_path, out_path, args.seed)
        except (OSError, ValueError) as exc:
            print(f"  FAILED: {exc}")
            failures += 1
            continue
        print(f"  done: {duration:.1f}s of audio")

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

