"""Corpus store: the on-disk dataset the fine-tuning studio manages.

A corpus lives in one directory:
    corpus/
        clips/                 validated WAV files (spkNN_RNNN.wav)
        manifest.csv           one row per accepted clip
        manifest.csv columns:  file, speaker_id, text, duration_s, verdict

Pure-Python, standard library only, so it is trivially testable and adds no
dependencies. The studio server is a thin HTTP layer over these functions.
"""

from __future__ import annotations

import csv
import shutil
from pathlib import Path

MANIFEST_COLUMNS = ["file", "speaker_id", "text", "duration_s", "verdict"]
TARGET_MINUTES = 60.0            # recommended minimum before fine-tuning
TARGET_SPEAKERS = 2              # recommended minimum distinct speakers


def manifest_path(corpus_dir: Path) -> Path:
    return Path(corpus_dir) / "manifest.csv"


def clips_dir(corpus_dir: Path) -> Path:
    return Path(corpus_dir) / "clips"


def load_manifest(corpus_dir: Path) -> list[dict]:
    """Return all accepted clips as a list of row dicts (empty if none)."""
    path = manifest_path(corpus_dir)
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def add_clip(
    corpus_dir: Path,
    src_wav: Path,
    speaker_id: str,
    text: str,
    duration_s: float,
    verdict: str,
) -> dict:
    """Copy a validated clip into the corpus and append a manifest row.

    The filename is derived from the speaker and the running clip count so the
    corpus is self-describing. Returns the new manifest row.
    """
    corpus_dir = Path(corpus_dir)
    clips_dir(corpus_dir).mkdir(parents=True, exist_ok=True)

    rows = load_manifest(corpus_dir)
    seq = sum(1 for r in rows if r["speaker_id"] == speaker_id) + 1
    filename = f"{speaker_id}_{seq:03d}.wav"
    shutil.copyfile(src_wav, clips_dir(corpus_dir) / filename)

    row = {
        "file": filename,
        "speaker_id": speaker_id,
        "text": text.replace("\n", " ").strip(),
        "duration_s": f"{float(duration_s):.2f}",
        "verdict": verdict,
    }
    path = manifest_path(corpus_dir)
    write_header = not path.exists()
    with path.open("a", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=MANIFEST_COLUMNS)
        if write_header:
            writer.writeheader()
        writer.writerow(row)
    return row


def stats(corpus_dir: Path) -> dict:
    """Compute the dashboard numbers from the manifest. Pure over the rows."""
    rows = load_manifest(corpus_dir)
    total_seconds = sum(float(r.get("duration_s", 0) or 0) for r in rows)
    per_speaker: dict[str, dict] = {}
    for r in rows:
        spk = r["speaker_id"]
        s = per_speaker.setdefault(spk, {"clips": 0, "seconds": 0.0})
        s["clips"] += 1
        s["seconds"] += float(r.get("duration_s", 0) or 0)

    minutes = total_seconds / 60.0
    speakers = len(per_speaker)
    ready = minutes >= TARGET_MINUTES and speakers >= TARGET_SPEAKERS

    return {
        "clips": len(rows),
        "minutes": round(minutes, 1),
        "speakers": speakers,
        "per_speaker": {
            spk: {"clips": v["clips"], "minutes": round(v["seconds"] / 60.0, 1)}
            for spk, v in sorted(per_speaker.items())
        },
        "target_minutes": TARGET_MINUTES,
        "target_speakers": TARGET_SPEAKERS,
        "ready_to_train": ready,
        "minutes_remaining": max(0.0, round(TARGET_MINUTES - minutes, 1)),
    }


def next_step_message(corpus_dir: Path) -> str:
    """A truthful, computed 'what to do next' line — never model-guessed."""
    s = stats(corpus_dir)
    if s["clips"] == 0:
        return ("No clips yet. Drop in WAV recordings from your voice actor and "
                "add the Kachin text each one reads.")
    if not s["ready_to_train"]:
        needs = []
        if s["minutes"] < s["target_minutes"]:
            needs.append(f"{s['minutes_remaining']} more minutes of audio")
        if s["speakers"] < s["target_speakers"]:
            needs.append(f"at least {s['target_speakers'] - s['speakers']} more speaker(s)")
        return (f"{s['clips']} clips, {s['minutes']} min from {s['speakers']} "
                f"speaker(s). To reach the training target you still need: "
                + ", and ".join(needs) + ".")
    return (f"Ready to train: {s['clips']} clips, {s['minutes']} min from "
            f"{s['speakers']} speakers. Export the dataset and run the sft/ pipeline.")


def export_training_manifest(corpus_dir: Path, out_path: Path) -> int:
    """Write a clean training manifest (accepted clips only). Returns row count.

    Format is the simple `path|text` layout most VITS/MMS fine-tuning scripts
    accept; adjust in sft/ if your trainer wants a different shape.
    """
    rows = load_manifest(corpus_dir)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(f"clips/{r['file']}|{r['text']}\n")
    return len(rows)

