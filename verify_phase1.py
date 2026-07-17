#!/usr/bin/env python3
"""Phase 1 verification for Kachin GPT.

Proves every claim the README makes about the core pipeline:

    1. All modules compile cleanly.
    2. The empty-input guard rejects blank text (no model required).
    3. The text chunker behaves (pure function, no model required).
    4. The vocabulary guard flags characters the voice cannot say.
    5. speak() returns valid 16 kHz int16 audio with real signal.

Run:  python verify_phase1.py          (full check; downloads model on first run)
      python verify_phase1.py --fast   (skips model inference -- checks 1-4 only)
"""

from __future__ import annotations

import py_compile
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))

RESULTS: list[tuple[str, bool, str]] = []


def check(name: str, passed: bool, detail: str = "") -> None:
    RESULTS.append((name, passed, detail))
    mark = "PASS" if passed else "FAIL"
    print(f"[{mark}] {name}" + (f" -- {detail}" if detail else ""))


def main() -> int:
    fast = "--fast" in sys.argv

    # 1. Modules compile
    modules = [
        "app/kachin_tts.py",
        "app/app.py",
        "tools/speak_file.py",
        "sft/recording-kit/check_recording.py",
        "llm/ollama_client.py",
        "verify_phase1.py",
    ]
    for module in modules:
        path = REPO_ROOT / module
        try:
            py_compile.compile(str(path), doraise=True)
            check(f"compile: {module}", True)
        except Exception as exc:  # noqa: BLE001
            check(f"compile: {module}", False, str(exc))

    from app.kachin_tts import SAMPLE_RATE, chunk_text, speak, unsupported_chars

    # 2. Empty-input guard (works without the ML stack)
    for bad_input in ["", "   ", "\n\t"]:
        try:
            speak(bad_input)
            check(f"empty-input guard rejects {bad_input!r}", False, "no error raised")
        except ValueError:
            check(f"empty-input guard rejects {bad_input!r}", True)
        except Exception as exc:  # noqa: BLE001
            check(f"empty-input guard rejects {bad_input!r}", False, f"wrong error: {exc}")

    # 3. Chunker
    chunks = chunk_text("Langai. Lahkawng. Masum.", max_chars=10)
    check("chunker splits long text", len(chunks) >= 2, f"{len(chunks)} chunks")
    check("chunker handles empty text", chunk_text("   ") == [])

    # 4. Vocabulary guard (pure logic; real tokenizer wired in check_text)
    vocab = set("kaji?")
    check("vocab guard passes covered text", unsupported_chars("Kaja ai i?", vocab) == [])
    check(
        "vocab guard flags unknown chars",
        unsupported_chars("Kaja 123", vocab) == ["1", "2", "3"],
    )

    # 4b. Assistant grounding is honest when nothing is verified
    sys.path.insert(0, str(REPO_ROOT / "llm"))
    from ollama_client import build_grounding_block
    check(
        "assistant grounding admits limits with no verified terms",
        "native speaker" in build_grounding_block([]).lower(),
    )

    # 5. Real synthesis
    if fast:
        print("\n--fast: skipping model inference checks.")
    else:
        import numpy as np

        audio, rate = speak("Chyeju kaba sai.")
        check("speak() sample rate is 16 kHz", rate == SAMPLE_RATE == 16_000, f"{rate} Hz")
        check("speak() returns int16 PCM", audio.dtype == np.int16, str(audio.dtype))
        check(
            "audio is non-trivial length",
            len(audio) > SAMPLE_RATE // 4,
            f"{len(audio)} samples",
        )
        check(
            "audio contains real signal",
            int(np.abs(audio).max()) > 500,
            f"peak amplitude {int(np.abs(audio).max())}",
        )
        audio_a, _ = speak("Kaja ai i?", seed=7)
        audio_b, _ = speak("Kaja ai i?", seed=7)
        check("seeded synthesis is reproducible", bool(np.array_equal(audio_a, audio_b)))

    failed = [r for r in RESULTS if not r[1]]
    print("\n" + "=" * 50)
    print(f"Phase 1 verification: {len(RESULTS) - len(failed)}/{len(RESULTS)} checks passed.")
    if failed:
        print("FAILED checks:")
        for name, _, detail in failed:
            print(f"  - {name} {detail}")
        return 1
    print("Phase 1: VERIFIED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
