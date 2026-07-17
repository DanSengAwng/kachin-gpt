"""Tests for the Kachin GPT core and field tools.

Fast tests run everywhere (CI included) with only numpy installed --
heavy ML dependencies are imported lazily by the modules under test.

The full synthesis test downloads the model (~145 MB) and runs only
when RUN_SLOW=1 is set:

    RUN_SLOW=1 pytest -q
"""

from __future__ import annotations

import csv
import os
import sys
import wave
from pathlib import Path

import numpy as np
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "sft" / "recording-kit"))
sys.path.insert(0, str(REPO_ROOT / "tools"))

from check_recording import analyze_wav  # noqa: E402
from speak_file import split_paragraphs  # noqa: E402

from app.kachin_tts import (  # noqa: E402
    SAMPLE_RATE,
    chunk_text,
    speak,
    unsupported_chars,
)

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


def test_unsupported_chars_covered_text() -> None:
    """Case-tolerant coverage: text fully in vocab reports nothing."""
    vocab = set("kaji?")
    assert unsupported_chars("Kaja ai i?", vocab) == []


def test_unsupported_chars_flags_unknown() -> None:
    vocab = set("kaji?")
    assert unsupported_chars("Kaja 123!", vocab) == ["!", "1", "2", "3"]


def test_unsupported_chars_ignores_whitespace() -> None:
    assert unsupported_chars("  \n\t ", set("a")) == []


def test_split_paragraphs() -> None:
    text = "First paragraph.\n\nSecond one.\n\n\n\nThird."
    assert split_paragraphs(text) == ["First paragraph.", "Second one.", "Third."]
    assert split_paragraphs("   \n\n  ") == []


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


# ------------------------------------------------- recording validator tests

def _write_wav(path: Path, audio: np.ndarray, rate: int = 16_000) -> None:
    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(rate)
        wav_file.writeframes(audio.astype(np.int16).tobytes())


def test_check_recording_accepts_clean_speechlike_audio(tmp_path: Path) -> None:
    t = np.linspace(0, 3.0, 3 * 16_000, endpoint=False)
    tone = (0.3 * np.sin(2 * np.pi * 220 * t) * 32767 * 0.5).astype(np.int16)
    path = tmp_path / "clean.wav"
    _write_wav(path, tone)
    result = analyze_wav(path)
    assert result["verdict"] in {"PASS", "WARN"}
    assert result["duration_s"] == pytest.approx(3.0, abs=0.05)
    assert result["clipping_pct"] < 0.1


def test_check_recording_flags_clipping(tmp_path: Path) -> None:
    clipped = np.full(2 * 16_000, 32767, dtype=np.int16)
    clipped[::2] = -32768
    path = tmp_path / "clipped.wav"
    _write_wav(path, clipped)
    result = analyze_wav(path)
    assert result["verdict"] == "FAIL"
    assert any("clipping" in issue for issue in result["issues"])


def test_check_recording_flags_too_short(tmp_path: Path) -> None:
    blip = (np.random.default_rng(0).normal(0, 3000, 4000)).astype(np.int16)
    path = tmp_path / "short.wav"
    _write_wav(path, blip)
    result = analyze_wav(path)
    assert result["verdict"] == "FAIL"
    assert any("short" in issue for issue in result["issues"])


# ---------------------------------------------------------------- slow tests

@pytest.mark.skipif(not RUN_SLOW, reason="set RUN_SLOW=1 to run model inference")
def test_speak_returns_valid_audio() -> None:
    audio, rate = speak("Chyeju kaba sai.")
    assert rate == SAMPLE_RATE == 16_000
    assert audio.dtype == np.int16
    assert len(audio) > SAMPLE_RATE // 4
    assert int(np.abs(audio).max()) > 500  # real signal, not silence


@pytest.mark.skipif(not RUN_SLOW, reason="set RUN_SLOW=1 to run model inference")
def test_speak_seed_is_reproducible() -> None:
    audio_a, _ = speak("Kaja ai i?", seed=7)
    audio_b, _ = speak("Kaja ai i?", seed=7)
    assert np.array_equal(audio_a, audio_b)


# ------------------------------------------------------- ollama adapter tests
# These test only the pure grounding logic -- no server is contacted.

sys.path.insert(0, str(REPO_ROOT / "llm"))
from ollama_client import (  # noqa: E402
    build_grounding_block,
    build_system_prompt,
    load_verified_terms,
)


def test_grounding_block_empty_is_honest() -> None:
    """With no verified terms, the prompt must admit the model can't do Kachin."""
    block = build_grounding_block([])
    assert "native speaker" in block.lower()


def test_grounding_block_lists_verified_terms() -> None:
    terms = [{"jinghpaw": "Kaja ai.", "english": "I am well.", "notes": ""}]
    block = build_grounding_block(terms)
    assert "Kaja ai." in block
    assert "I am well." in block


def test_system_prompt_enforces_review() -> None:
    prompt = build_system_prompt([])
    assert "review" in prompt.lower()
    assert "native speaker" in prompt.lower()


def test_load_verified_terms_gates_on_flag(tmp_path: Path) -> None:
    """Only rows with verified == 'true' are returned for grounding."""
    csv_path = tmp_path / "tb.csv"
    csv_path.write_text(
        "jinghpaw,english,domain,notes,verified\n"
        "Kaja ai.,I am well.,greetings,,true\n"
        "Guess.,unknown,greetings,,false\n",
        encoding="utf-8",
    )
    verified = load_verified_terms(csv_path)
    assert len(verified) == 1
    assert verified[0]["jinghpaw"] == "Kaja ai."
