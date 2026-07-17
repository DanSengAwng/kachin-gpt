"""Free, local, offline LLM access via Ollama -- no API key, no cost.

Talks to a locally running Ollama server (default http://localhost:11434)
using only the Python standard library, so it adds nothing to
`requirements.txt`. The model is configurable; point it at whatever you
have pulled:

    ollama pull llama3.2          # then set OLLAMA_MODEL=llama3.2
    OLLAMA_MODEL=qwen2.5 python -m llm.ollama_client "Greet a visitor"

Honesty first: general local models are weak at Kachin (a low-resource
language). This layer therefore GROUNDS every request in the verified
terminology bank and labels output as unreviewed. It is an assistant for
drafting, never an authority -- the verbatim TTS core is what you trust
for exact text.
"""

from __future__ import annotations

import csv
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
TERMBANK_PATH = REPO_ROOT / "termbank" / "termbank.csv"


class OllamaUnavailable(RuntimeError):
    """Raised when the local Ollama server cannot be reached."""


def load_verified_terms(path: Path = TERMBANK_PATH) -> list[dict]:
    """Return only termbank rows a native speaker has verified.

    Grounding must never be built on unreviewed machine guesses, so
    ``verified == 'true'`` is the gate. Pure function (file in, list out).
    """
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    return [r for r in rows if r.get("verified", "false").strip().lower() == "true"]


def build_grounding_block(terms: list[dict]) -> str:
    """Format verified terms as a reference block for the system prompt."""
    if not terms:
        return (
            "No Kachin terms have been verified by a native speaker yet. "
            "You do not reliably know Kachin. If asked to produce Kachin, "
            "say plainly that it must be reviewed by a native speaker."
        )
    lines = [
        f"- {t['jinghpaw']} = {t['english']}"
        + (f" ({t['notes']})" if t.get("notes") else "")
        for t in terms
    ]
    return (
        "Verified Kachin (Jinghpaw) terms you may rely on -- use these "
        "exactly, do not alter their spelling:\n" + "\n".join(lines)
    )


def build_system_prompt(terms: list[dict]) -> str:
    """Assemble the grounded, honesty-first system prompt."""
    return (
        "You assist with the Kachin (Jinghpaw) language for a community "
        "preservation project. Kachin is low-resource and you are not "
        "fluent in it. Rules:\n"
        "1. Prefer the verified terms below; use them verbatim.\n"
        "2. If you are not confident a Kachin word is correct, say so "
        "explicitly rather than guessing.\n"
        "3. Never present unverified Kachin as authoritative. Everything "
        "you generate must be reviewed by a native speaker before use.\n\n"
        + build_grounding_block(terms)
    )


def generate(
    prompt: str,
    model: str | None = None,
    host: str | None = None,
    timeout: float = 60.0,
) -> str:
    """Send a grounded prompt to the local Ollama model and return text.

    Raises:
        OllamaUnavailable: if the server is not reachable (e.g. Ollama is
            not running). The caller decides how to degrade -- the TTS
            core keeps working regardless.
    """
    model = model or DEFAULT_MODEL
    host = (host or DEFAULT_HOST).rstrip("/")
    system = build_system_prompt(load_verified_terms())

    payload = json.dumps({
        "model": model,
        "prompt": prompt,
        "system": system,
        "stream": False,
    }).encode("utf-8")

    request = urllib.request.Request(
        f"{host}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise OllamaUnavailable(
            f"Cannot reach Ollama at {host}. Is it running? "
            f"Start it with `ollama serve` and `ollama pull {model}`. "
            f"({exc})"
        ) from exc
    return data.get("response", "").strip()


def is_available(host: str | None = None, timeout: float = 3.0) -> bool:
    """Quick check: is a local Ollama server reachable right now?"""
    host = (host or DEFAULT_HOST).rstrip("/")
    try:
        urllib.request.urlopen(f"{host}/api/tags", timeout=timeout)
        return True
    except urllib.error.URLError:
        return False


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: python -m llm.ollama_client \"your prompt\"")
        return 2
    prompt = " ".join(sys.argv[1:])
    try:
        print(generate(prompt))
    except OllamaUnavailable as exc:
        print(f"[assistant unavailable] {exc}")
        print("The verbatim text-to-speech core does not need this and "
              "still works offline.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

