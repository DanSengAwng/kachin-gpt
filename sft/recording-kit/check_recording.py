#!/usr/bin/env python3
"""Validate community recordings before they enter the fine-tuning corpus.

Checks each WAV file for the problems that actually ruin training data:
wrong format, clipping, silence padding, and too-quiet recordings.

Usage:

    python sft/recording-kit/check_recording.py recordings/*.wav

Phone recordings are usually .m4a -- convert to WAV first:

    ffmpeg -i clip.m4a -ar 16000 -ac 1 clip.wav

Exit code 0 = no failures; 1 = at least one FAIL.
"""

from __future__ import annotations

import argparse
import wave
from pathlib import Path

import numpy as np

TARGET_RATE = 16_000
MIN_DURATION_S = 1.0
MAX_DURATION_S = 60.0
CLIPPING_FAIL_PCT = 1.0     # % of samples at full scale
QUIET_WARN_DBFS = -35.0
QUIET_FAIL_DBFS = -45.0
EDGE_SILENCE_WARN_S = 2.0


def analyze_wav(path: Path) -> dict:
    """Analyze one WAV file. Returns a dict with metrics, issues, verdict."""
    issues: list[str] = []
    verdict = "PASS"

    def warn(msg: str) -> None:
        nonlocal verdict
        issues.append(f"WARN: {msg}")
        if verdict == "PASS":
            verdict = "WARN"

    def fail(msg: str) -> None:
        nonlocal verdict
        issues.append(f"FAIL: {msg}")
        verdict = "FAIL"

    try:
        with wave.open(str(path), "rb") as wav_file:
            n_channels = wav_file.getnchannels()
            rate = wav_file.getframerate()
            sample_width = wav_file.getsampwidth()
            n_frames = wav_file.getnframes()
            raw = wav_file.readframes(n_frames)
    except (OSError, wave.Error) as exc:
        return {"path": str(path), "verdict": "FAIL",
                "issues": [f"FAIL: unreadable ({exc})"]}

    if sample_width != 2:
        fail(f"sample width {sample_width * 8}-bit; expected 16-bit PCM")
        return {"path": str(path), "verdict": verdict, "issues": issues}

    audio = np.frombuffer(raw, dtype=np.int16).astype(np.float32)
    if n_channels > 1:
        warn(f"{n_channels} channels; will be downmixed to mono")
        audio = audio.reshape(-1, n_channels).mean(axis=1)

    duration = len(audio) / rate if rate else 0.0
    if duration < MIN_DURATION_S:
        fail(f"too short ({duration:.2f}s); aim for {MIN_DURATION_S:.0f}-{MAX_DURATION_S:.0f}s per clip")
    elif duration > MAX_DURATION_S:
        fail(f"too long ({duration:.1f}s); split into shorter clips")

    if rate != TARGET_RATE:
        warn(f"sample rate {rate} Hz; will be resampled to {TARGET_RATE} Hz")

    peak = float(np.abs(audio).max()) if len(audio) else 0.0
    clipping_pct = 100.0 * float(np.mean(np.abs(audio) >= 32766)) if len(audio) else 0.0
    if clipping_pct > CLIPPING_FAIL_PCT:
        fail(f"clipping on {clipping_pct:.1f}% of samples; re-record further from the mic")
    elif clipping_pct > 0.1:
        warn(f"some clipping ({clipping_pct:.2f}% of samples)")

    rms = float(np.sqrt(np.mean(np.square(audio)))) if len(audio) else 0.0
    rms_dbfs = 20 * np.log10(rms / 32768.0) if rms > 0 else -120.0
    if rms_dbfs < QUIET_FAIL_DBFS:
        fail(f"too quiet ({rms_dbfs:.1f} dBFS); move closer to the mic")
    elif rms_dbfs < QUIET_WARN_DBFS:
        warn(f"quiet recording ({rms_dbfs:.1f} dBFS)")

    # Leading/trailing silence: 50 ms frames below a low energy threshold.
    frame = max(1, int(0.05 * rate))
    threshold = max(rms * 0.05, 100.0)
    n_full_frames = len(audio) // frame
    silent = [
        float(np.sqrt(np.mean(np.square(audio[i * frame:(i + 1) * frame])))) < threshold
        for i in range(n_full_frames)
    ]
    lead = 0
    for is_silent in silent:
        if not is_silent:
            break
        lead += 1
    tail = 0
    for is_silent in reversed(silent):
        if not is_silent:
            break
        tail += 1
    lead_s, tail_s = lead * 0.05, tail * 0.05
    if lead_s > EDGE_SILENCE_WARN_S or tail_s > EDGE_SILENCE_WARN_S:
        warn(f"long silence at edges (lead {lead_s:.1f}s / tail {tail_s:.1f}s); will be trimmed")

    return {
        "path": str(path), "verdict": verdict, "issues": issues,
        "duration_s": round(duration, 2), "sample_rate": rate,
        "channels": n_channels, "peak": int(peak),
        "clipping_pct": round(clipping_pct, 2), "rms_dbfs": round(rms_dbfs, 1),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate recording WAV files.")
    parser.add_argument("files", nargs="+", type=Path)
    args = parser.parse_args()

    counts = {"PASS": 0, "WARN": 0, "FAIL": 0}
    for path in args.files:
        result = analyze_wav(path)
        counts[result["verdict"]] += 1
        print(f"[{result['verdict']}] {path}")
        for issue in result["issues"]:
            print(f"    {issue}")

    total = sum(counts.values())
    print(f"\n{total} file(s): {counts['PASS']} pass, "
          f"{counts['WARN']} warn, {counts['FAIL']} fail")
    return 1 if counts["FAIL"] else 0


if __name__ == "__main__":
    raise SystemExit(main())

