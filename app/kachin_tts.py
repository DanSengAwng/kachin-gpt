"""Kachin (Jingpho) text-to-speech core.

Wraps Meta's Massively Multilingual Speech model for Kachin
(``facebook/mms-tts-kac``) behind a small, verified API.

Design notes:
    - Heavy dependencies (torch, transformers) are imported lazily inside
      functions, so this module can be imported -- and its input guards
      tested -- without the ML stack installed.
    - ``speak()`` is the single public synthesis entry point. Everything
      it claims is checked by ``verify_phase1.py`` and ``tests/``.
    - Verbatim by design: this module reads exactly the text it is given.
      No text is generated, expanded, or altered.
"""

from __future__ import annotations

import re
import warnings
import wave
from pathlib import Path

import numpy as np

MODEL_ID = "facebook/mms-tts-kac"
SAMPLE_RATE = 16_000  # asserted against model config at load time

# Pause inserted between chunks of long text (seconds of silence).
_CHUNK_PAUSE_S = 0.25

# Cached model/tokenizer pair -- loaded once per process.
_MODEL_CACHE: dict = {}


def chunk_text(text: str, max_chars: int = 200) -> list[str]:
    """Split long text into speakable chunks on sentence boundaries.

    Keeps each chunk under ``max_chars`` where possible, splitting on
    sentence-ending punctuation and newlines. Pure function -- unit
    tested without the model.
    """
    pieces = [p.strip() for p in re.split(r"(?<=[.!?])\s+|\n+", text) if p.strip()]
    if not pieces:
        return []

    chunks: list[str] = []
    current = ""
    for piece in pieces:
        candidate = f"{current} {piece}".strip()
        if current and len(candidate) > max_chars:
            chunks.append(current)
            current = piece
        else:
            current = candidate
    if current:
        chunks.append(current)
    return chunks


def unsupported_chars(text: str, vocab: set[str]) -> list[str]:
    """Characters in ``text`` not covered by ``vocab`` (case-tolerant).

    Whitespace is ignored. Pure function -- unit tested without the
    model; ``check_text()`` supplies the real tokenizer vocabulary.
    """
    missing = []
    for ch in text:
        if ch.isspace():
            continue
        if ch in vocab or ch.lower() in vocab:
            continue
        missing.append(ch)
    return sorted(set(missing))


def check_text(text: str) -> list[str]:
    """Best-effort list of characters the voice model will likely skip.

    The MMS tokenizer silently drops characters outside its alphabet,
    which produces subtly wrong audio. This surfaces the problem instead
    of hiding it. Loads the tokenizer on first call.
    """
    _, tokenizer = _load()
    vocab = set(tokenizer.get_vocab().keys())
    return unsupported_chars(text, vocab)


def _load():
    """Load and cache the MMS Kachin model + tokenizer (first call only)."""
    if "model" not in _MODEL_CACHE:
        import torch  # noqa: F401  (fail fast if the ML stack is missing)
        from transformers import AutoTokenizer, VitsModel

        model = VitsModel.from_pretrained(MODEL_ID)
        tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
        model.eval()

        configured_rate = getattr(model.config, "sampling_rate", SAMPLE_RATE)
        if configured_rate != SAMPLE_RATE:
            raise RuntimeError(
                f"Model sampling rate {configured_rate} != expected {SAMPLE_RATE}"
            )

        _MODEL_CACHE["model"] = model
        _MODEL_CACHE["tokenizer"] = tokenizer
    return _MODEL_CACHE["model"], _MODEL_CACHE["tokenizer"]


def warm_up() -> None:
    """Load the model and run one short synthesis so the first real
    request is fast. Call at app startup."""
    _load()
    _synthesize_chunk("a")


def _synthesize_chunk(text: str) -> np.ndarray:
    """Synthesize one chunk of Kachin text -> float waveform in [-1, 1]."""
    import torch

    model, tokenizer = _load()
    inputs = tokenizer(text, return_tensors="pt")
    with torch.no_grad():
        waveform = model(**inputs).waveform
    return waveform.squeeze().cpu().numpy()


def speak(text: str, seed: int | None = None) -> tuple[np.ndarray, int]:
    """Synthesize Kachin speech from text.

    Args:
        text: Kachin (Jingpho) text in Latin script.
        seed: Optional random seed. The VITS duration predictor is
            stochastic, so the same text normally produces slightly
            different audio each run; pass a seed for reproducible
            output (same text + seed + library versions -> same audio).

    Returns:
        (audio, sample_rate): 16-bit PCM waveform as an int16 numpy
        array, and the sample rate (16,000 Hz).

    Raises:
        ValueError: if ``text`` is empty or whitespace-only.

    Warns:
        UserWarning: if the text contains characters outside the voice
        model's alphabet (they would be silently skipped by the model).
    """
    if not text or not text.strip():
        raise ValueError("Input text is empty -- nothing to synthesize.")

    missing = check_text(text)
    if missing:
        warnings.warn(
            "These characters are outside the voice model's alphabet and "
            f"will likely be skipped: {missing}",
            stacklevel=2,
        )

    if seed is not None:
        import torch

        torch.manual_seed(seed)

    chunks = chunk_text(text)
    pause = np.zeros(int(_CHUNK_PAUSE_S * SAMPLE_RATE), dtype=np.float32)

    parts: list[np.ndarray] = []
    for i, chunk in enumerate(chunks):
        if i > 0:
            parts.append(pause)
        parts.append(_synthesize_chunk(chunk).astype(np.float32))

    audio_float = np.concatenate(parts)
    audio_int16 = (np.clip(audio_float, -1.0, 1.0) * 32767).astype(np.int16)
    return audio_int16, SAMPLE_RATE


def save_wav(text: str, path: str | Path, seed: int | None = None) -> Path:
    """Synthesize ``text`` and write a 16-bit mono WAV file to ``path``."""
    audio, rate = speak(text, seed=seed)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)  # int16
        wav_file.setframerate(rate)
        wav_file.writeframes(audio.tobytes())
    return path
