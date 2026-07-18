"""Kachin GPT Fine-Tuning Studio -- local web app for corpus building.

A single-machine tool the people preparing fine-tuning data actually use:
drop in your voice actor's recordings, get each one validated, pair it with
its Kachin text, watch the corpus grow toward the training target, and ask a
built-in assistant (your local Ollama model) for guidance -- then export a
clean, training-ready dataset for the sft/ pipeline.

Runs locally so it can do real work (audio validation, filesystem, Ollama) and
so raw voice recordings + consent stay on the contributor's own machine.

    pip install -r studio/requirements.txt
    python studio/server.py           # then open http://localhost:8000

Everything heavy is reused from the rest of the repo:
    sft/recording-kit/check_recording.py  -> real audio validation
    llm/ollama_client.py                  -> free local assistant
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "sft" / "recording-kit"))
sys.path.insert(0, str(REPO_ROOT / "llm"))
sys.path.insert(0, str(REPO_ROOT / "studio"))

import uvicorn  # noqa: E402
from fastapi import FastAPI, Form, UploadFile  # noqa: E402
from fastapi.responses import FileResponse, JSONResponse  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402

import corpus_store as store  # noqa: E402
from check_recording import analyze_wav  # noqa: E402

CORPUS_DIR = Path(__file__).resolve().parent / "corpus"
STATIC_DIR = Path(__file__).resolve().parent / "static"

app = FastAPI(title="Kachin GPT Fine-Tuning Studio")


@app.get("/api/health")
def health() -> dict:
    """Backend + Ollama availability, so the UI can show honest status."""
    ollama_up = False
    model = None
    try:
        import ollama_client
        ollama_up = ollama_client.is_available()
        model = ollama_client.DEFAULT_MODEL
    except Exception:  # noqa: BLE001
        ollama_up = False
    return {"ok": True, "ollama": ollama_up, "ollama_model": model}


@app.get("/api/corpus")
def corpus() -> dict:
    """Dashboard numbers + the truthful next-step line."""
    data = store.stats(CORPUS_DIR)
    data["next_step"] = store.next_step_message(CORPUS_DIR)
    return data


@app.post("/api/validate")
async def validate(clip: UploadFile) -> JSONResponse:
    """Run the real recording validator on an uploaded WAV. No corpus change."""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(await clip.read())
        tmp_path = Path(tmp.name)
    try:
        result = analyze_wav(tmp_path)
    finally:
        tmp_path.unlink(missing_ok=True)
    result["filename"] = clip.filename
    return JSONResponse(result)


@app.post("/api/add")
async def add(
    clip: UploadFile,
    speaker_id: str = Form(...),
    text: str = Form(...),
) -> JSONResponse:
    """Validate, then (only if not a FAIL) add the clip to the corpus."""
    if not text.strip():
        return JSONResponse({"error": "Transcript text is required."}, status_code=400)

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(await clip.read())
        tmp_path = Path(tmp.name)
    try:
        result = analyze_wav(tmp_path)
        if result["verdict"] == "FAIL":
            return JSONResponse(
                {"error": "Clip failed validation; not added.", "result": result},
                status_code=422,
            )
        row = store.add_clip(
            CORPUS_DIR, tmp_path,
            speaker_id=speaker_id.strip() or "spk01",
            text=text,
            duration_s=result.get("duration_s", 0.0),
            verdict=result["verdict"],
        )
    finally:
        tmp_path.unlink(missing_ok=True)

    return JSONResponse({"added": row, "result": result, "corpus": corpus()})


@app.post("/api/chat")
async def chat(message: str = Form(...)) -> JSONResponse:
    """Assistant reply. Always prepend the TRUE corpus status (computed, not
    guessed), then let the local model answer the question if it is running."""
    status_line = store.next_step_message(CORPUS_DIR)
    reply = status_line
    try:
        import ollama_client
        if ollama_client.is_available():
            prompt = (
                "You are helping someone prepare voice recordings to fine-tune a "
                "Kachin text-to-speech model. Be brief and practical. "
                f"Current corpus status (authoritative, do not contradict): {status_line}\n\n"
                f"Their message: {message}"
            )
            model_reply = ollama_client.generate(prompt)
            if model_reply:
                reply = model_reply + "\n\n---\nCorpus status: " + status_line
    except Exception:  # noqa: BLE001
        reply = (status_line + "\n\n(The local assistant is offline. Start it with "
                 "`ollama serve` for conversational help; the studio still works.)")
    return JSONResponse({"reply": reply})


@app.post("/api/export")
def export() -> JSONResponse:
    """Write the training manifest next to the corpus and report the path."""
    out = CORPUS_DIR / "train_manifest.txt"
    n = store.export_training_manifest(CORPUS_DIR, out)
    return JSONResponse({
        "rows": n,
        "path": str(out),
        "hint": "Point the sft/ fine-tuning pipeline at corpus/clips/ + this manifest.",
    })


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


# Serve the rest of static/ (kept after routes so /api/* wins).
app.mount("/", StaticFiles(directory=str(STATIC_DIR)), name="static")


if __name__ == "__main__":
    CORPUS_DIR.mkdir(parents=True, exist_ok=True)
    print("Kachin GPT Fine-Tuning Studio -> http://localhost:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)

