"""Acceptance goalposts for BACKLOG.md tasks -- skip-marked until implemented.

Protocol (AGENT_LOOP.md): pick a task, remove ONLY its skip marker, implement
until green. Task-specific imports live inside the tests so collection never
breaks before the code exists. Do not edit assertions.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.skip(reason="T01: unskip when implementing query grounding")
def test_t01_query_grounding() -> None:
    sys.path.insert(0, str(REPO_ROOT / "llm"))
    from ollama_client import build_query_grounding

    block = build_query_grounding("thank you", k=3)
    # retrieval must surface the matching seed row...
    assert "Chyeju" in block
    # ...and unverified rows must be labeled as such (seeds are unverified
    # until H01 happens; if H01 verified them all, adapt the fixture, not this rule).
    assert "unverified" in block.lower() or "needs native review" in block.lower()


@pytest.mark.skip(reason="T02: unskip when implementing remove_clip")
def test_t02_remove_clip(tmp_path: Path) -> None:
    import wave

    import numpy as np
    sys.path.insert(0, str(REPO_ROOT / "studio"))
    import corpus_store as store

    src = tmp_path / "s.wav"
    audio = (np.zeros(16000) + 3000).astype(np.int16)
    with wave.open(str(src), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(16000)
        w.writeframes(audio.tobytes())

    store.add_clip(tmp_path, src, "spk01", "one", 1.0, "PASS")
    store.add_clip(tmp_path, src, "spk01", "two", 1.0, "PASS")

    assert store.remove_clip(tmp_path, "spk01_001.wav") is True
    assert not (store.clips_dir(tmp_path) / "spk01_001.wav").exists()
    rows = store.load_manifest(tmp_path)
    assert [r["file"] for r in rows] == ["spk01_002.wav"]
    # sequence keeps counting up -- no filename reuse after deletion
    third = store.add_clip(tmp_path, src, "spk01", "three", 1.0, "PASS")
    assert third["file"] == "spk01_002.wav" or third["file"] == "spk01_003.wav"
    assert store.remove_clip(tmp_path, "nope.wav") is False


@pytest.mark.skip(reason="T03: unskip when implementing the number normalizer")
def test_t03_number_normalizer() -> None:
    from app.normalize import number_to_jinghpaw

    numerals = {1: "langai", 2: "lahkawng", 3: "masum"}
    assert number_to_jinghpaw(2, numerals) == "lahkawng"
    with pytest.raises(NotImplementedError):
        number_to_jinghpaw(7, numerals)  # unknown -> honest gap, never a guess


@pytest.mark.skip(reason="T06: unskip when implementing the MOS sheet generator")
def test_t06_mos_sheet() -> None:
    sys.path.insert(0, str(REPO_ROOT / "tools"))
    from mos_sheet import make_mos_rows

    manifest = [{"file": f"spk01_{i:03d}.wav", "text": f"t{i}"} for i in range(1, 6)]
    rows = make_mos_rows(manifest, seed=0)
    assert len(rows) == 5
    assert {"file", "text", "naturalness_1to5", "intelligibility_1to5", "notes"} \
        <= set(rows[0].keys())
    assert all(r["naturalness_1to5"] == "" for r in rows)  # blank for the listener
    # deterministic shuffle for a given seed
    assert [r["file"] for r in make_mos_rows(manifest, seed=0)] \
        == [r["file"] for r in rows]
