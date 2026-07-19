"""BM25 retrieval over the terminology bank -- Phase 3, first live component.

Pure Python, standard library only, transparent by design (see BLUEPRINT.md
decision log: BM25 over embeddings while the corpus is small). Verified rows
get a modest score boost so curated data outranks unreviewed seeds.

    from rag.retrieve import search
    hits = search("thank you")          # -> [{"row": {...}, "score": 3.2}, ...]
"""

from __future__ import annotations

import csv
import math
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TERMBANK_PATH = REPO_ROOT / "termbank" / "termbank.csv"

K1 = 1.5              # BM25 term-frequency saturation
B = 0.75              # BM25 length normalization
VERIFIED_BOOST = 1.25  # native-speaker-reviewed rows rank above seeds

_SEARCH_FIELDS = ("jinghpaw", "english", "domain", "notes")


def tokenize(text: str) -> list[str]:
    """Lowercase word tokens (letters, digits, apostrophes). Pure function."""
    return re.findall(r"[a-z0-9']+", text.lower())


def load_rows(path: Path = TERMBANK_PATH) -> list[dict]:
    """All termbank rows (verified or not); empty list if file is missing."""
    path = Path(path)
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def _doc_tokens(row: dict) -> list[str]:
    return tokenize(" ".join(row.get(field, "") or "" for field in _SEARCH_FIELDS))


def search(
    query: str,
    rows: list[dict] | None = None,
    k: int = 5,
    path: Path = TERMBANK_PATH,
) -> list[dict]:
    """Top-k termbank rows for ``query``, best first.

    Returns [{"row": <termbank row>, "score": float}, ...]. Rows with zero
    overlap are omitted; empty query or empty termbank -> [].
    """
    if rows is None:
        rows = load_rows(path)
    query_tokens = tokenize(query)
    if not query_tokens or not rows:
        return []

    docs = [_doc_tokens(row) for row in rows]
    n_docs = len(docs)
    avg_len = sum(len(d) for d in docs) / n_docs

    doc_freq: dict[str, int] = {}
    for doc in docs:
        for term in set(doc):
            doc_freq[term] = doc_freq.get(term, 0) + 1

    hits: list[dict] = []
    for row, doc in zip(rows, docs):
        term_freq: dict[str, int] = {}
        for term in doc:
            term_freq[term] = term_freq.get(term, 0) + 1

        score = 0.0
        for term in query_tokens:
            tf = term_freq.get(term)
            if not tf:
                continue
            df = doc_freq[term]
            idf = math.log(1 + (n_docs - df + 0.5) / (df + 0.5))
            norm = tf * (K1 + 1) / (tf + K1 * (1 - B + B * len(doc) / avg_len))
            score += idf * norm

        if score <= 0:
            continue
        if (row.get("verified", "") or "").strip().lower() == "true":
            score *= VERIFIED_BOOST
        hits.append({"row": row, "score": round(score, 4)})

    hits.sort(key=lambda h: -h["score"])
    return hits[:k]
