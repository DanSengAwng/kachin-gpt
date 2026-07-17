"""Tests for the Kachin GPT core.

Fast tests run everywhere (CI included) with only numpy installed --
heavy ML dependencies are imported lazily by the module under test.

The full synthesis test downloads the model (~145 MB) and runs only
when RUN_SLOW=1 is set:

    RUN_SLOW=1 pytest -q
"""

from __future__ import annotations

import csv
import os
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from app.kachin_tts import SAMPLE_RATE, chunk_text, speak  # noqa: E402

RUN_SLOW = os.getenv("RUN_SLOW") == "1"


# ---------------------------------------------------------------- fast tests

@pytest.mark.parametrize("bad_input", ["", "   ", "\n\t "])
def test_empty_input_raises(bad_input: str) -> None:
    """The guard must reject blank input before touching the model."""
    with pytest.raises(ValueError):
        speak(bad_input)


def test_chunker_splits_on_sentences() -> None:
    chunks = chunk_text("Langai. Lahkawng. Masum. Mali. Manga.", max_chars=12)
    assert len(chunks) >= 2
    assert all(chunk.strip() for chunk in chunks)


def test_chunker_preserves_short_text() -> None:
    assert chunk_text("Kaja ai i?") == ["Kaja ai i?"]


def test_chunker_empty() -> None:
    assert chunk_text("") == []
    assert chunk_text("  \n ") == []


def test_termbank_schema() -> None:
    """Seed termbank must load and carry the review-workflow columns."""
    termbank = REPO_ROOT / "termbank" / "termbank.csv"
    with termbank.open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    assert rows, "termbank should not be empty"
    required = {"jinghpaw", "english", "domain", "verified"}
    assert required.issubset(rows[0].keys())
    # Honesty invariant: entries are explicitly marked reviewed or not.
    assert all(row["verified"] in {"true", "false"} for row in rows)


# ---------------------------------------------------------------- slow tests

@pytest.mark.skipif(not RUN_SLOW, reason="set RUN_SLOW=1 to run model inference")
def test_speak_returns_valid_audio() -> None:
    import numpy as np

    audio, rate = speak("Chyeju kaba sai.")
    assert rate == SAMPLE_RATE == 16_000
    assert audio.dtype == np.int16
    assert len(audio) > SAMPLE_RATE // 4
    assert int(np.abs(audio).max()) > 500  # real signal, not silence

