# Grounded Language Layer (design — Phase 3)

No frontier LLM handles Kachin well: it is a low-resource language, and
ungrounded generation produces confident nonsense. This layer is the design
response — retrieval grounding over community-curated data.

## Architecture

```
user request (English or Kachin)
        │
        ▼
retrieve top-k termbank entries        ←  termbank/termbank.csv
(BM25 keyword match; embeddings later)    (verified entries preferred)
        │
        ▼
Claude drafts Kachin text with retrieved
terms pinned in the system prompt
        │
        ▼
confidence gate:
  - terms found in termbank → used verbatim
  - no coverage → output flagged as unreviewed,
    English fallback shown alongside
        │
        ▼
app/kachin_tts.speak()  →  audio
```

## Design decisions

- **BM25 before embeddings.** The termbank is small and keyword-shaped;
  classical retrieval is transparent, dependency-free, and easy to debug.
  Embeddings become worthwhile when the corpus outgrows exact-match recall.
- **Grounding beats generation.** For names, places, and domain vocabulary
  the retrieved term is used verbatim — the model fills grammar around it,
  not the other way around.
- **Honest low-confidence behavior.** When the termbank has no coverage,
  the UI says so. A wrong-but-confident answer in a language-preservation
  tool damages exactly the trust the project depends on.

## Status

Design complete; implementation begins alongside Phase 2 data collection.
The termbank schema (with its `verified` flag) is already live and consumed
by the test suite.

