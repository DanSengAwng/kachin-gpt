"""Tests for BM25 termbank retrieval (pure Python, no ML stack)."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from rag.retrieve import load_rows, search, tokenize  # noqa: E402


def _row(jinghpaw: str, english: str, verified: str = "false", domain: str = "x") -> dict:
    return {"jinghpaw": jinghpaw, "english": english, "domain": domain,
            "notes": "", "verified": verified}


def test_tokenize_basic() -> None:
    assert tokenize("Chyeju kaba sai!") == ["chyeju", "kaba", "sai"]
    assert tokenize("") == []


def test_search_finds_matching_row() -> None:
    rows = [_row("Myitkyina", "capital of Kachin State"),
            _row("Kaja ai.", "I am well.")]
    hits = search("myitkyina", rows=rows)
    assert hits and hits[0]["row"]["jinghpaw"] == "Myitkyina"


def test_search_matches_english_gloss() -> None:
    rows = [_row("Chyeju kaba sai.", "Thank you very much."),
            _row("jan", "sun")]
    hits = search("thank you", rows=rows)
    assert hits and hits[0]["row"]["jinghpaw"] == "Chyeju kaba sai."


def test_verified_rows_rank_first_on_ties() -> None:
    rows = [_row("kaja A", "well", verified="false"),
            _row("kaja B", "well", verified="true")]
    hits = search("kaja", rows=rows)
    assert hits[0]["row"]["jinghpaw"] == "kaja B"


def test_k_limits_results() -> None:
    rows = [_row(f"kaja {i}", "well") for i in range(10)]
    assert len(search("kaja", rows=rows, k=3)) == 3


def test_empty_query_and_missing_file() -> None:
    assert search("", rows=[_row("a", "b")]) == []
    assert search("anything", path=Path("/nonexistent/tb.csv")) == []


def test_search_real_termbank() -> None:
    """Integration: the shipped seed termbank is findable."""
    rows = load_rows()
    assert rows, "seed termbank should load"
    hits = search("thank")
    assert hits and "Chyeju" in hits[0]["row"]["jinghpaw"]
