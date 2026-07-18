"""Tests for the fine-tuning studio's corpus store (pure, no server, no deps)."""

from __future__ import annotations

import sys
import wave
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "studio"))

import corpus_store as store  # noqa: E402


def _wav(path: Path, seconds: float) -> None:
    rate = 16_000
    samples = np.linspace(0, seconds, int(seconds * rate), endpoint=False)
    audio = (0.2 * np.sin(2 * np.pi * 180 * samples) * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(audio.tobytes())


def test_empty_corpus_stats(tmp_path: Path) -> None:
    s = store.stats(tmp_path)
    assert s["clips"] == 0
    assert s["minutes"] == 0.0
    assert s["speakers"] == 0
    assert s["ready_to_train"] is False
    assert "No clips yet" in store.next_step_message(tmp_path)


def test_add_clip_and_stats(tmp_path: Path) -> None:
    src = tmp_path / "src.wav"
    _wav(src, 2.0)
    row = store.add_clip(tmp_path, src, speaker_id="spk01", text="Kaja ai.",
                         duration_s=2.0, verdict="PASS")
    assert row["file"] == "spk01_001.wav"
    assert (store.clips_dir(tmp_path) / "spk01_001.wav").exists()

    s = store.stats(tmp_path)
    assert s["clips"] == 1
    assert s["speakers"] == 1
    assert s["per_speaker"]["spk01"]["clips"] == 1


def test_sequential_filenames_per_speaker(tmp_path: Path) -> None:
    src = tmp_path / "s.wav"
    _wav(src, 1.5)
    a = store.add_clip(tmp_path, src, "spk01", "one", 1.5, "PASS")
    b = store.add_clip(tmp_path, src, "spk01", "two", 1.5, "PASS")
    c = store.add_clip(tmp_path, src, "spk02", "three", 1.5, "PASS")
    assert a["file"] == "spk01_001.wav"
    assert b["file"] == "spk01_002.wav"
    assert c["file"] == "spk02_001.wav"


def test_ready_flag_needs_minutes_and_speakers(tmp_path: Path) -> None:
    src = tmp_path / "s.wav"
    _wav(src, 1.0)
    store.add_clip(tmp_path, src, "spk01", "x", store.TARGET_MINUTES * 60, "PASS")
    assert store.stats(tmp_path)["ready_to_train"] is False  # only 1 speaker
    store.add_clip(tmp_path, src, "spk02", "y", store.TARGET_MINUTES * 60, "PASS")
    assert store.stats(tmp_path)["ready_to_train"] is True


def test_export_manifest_format(tmp_path: Path) -> None:
    src = tmp_path / "s.wav"
    _wav(src, 1.0)
    store.add_clip(tmp_path, src, "spk01", "Chyeju kaba sai.", 1.0, "PASS")
    out = tmp_path / "train.txt"
    n = store.export_training_manifest(tmp_path, out)
    assert n == 1
    assert out.read_text().strip() == "clips/spk01_001.wav|Chyeju kaba sai."

