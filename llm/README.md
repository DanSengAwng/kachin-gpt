# Optional Assistant Layer -- Local & Free (Ollama)

This directory adds an **optional** assistant that can draft or explain
Kachin text using a **free local model** through
[Ollama](https://ollama.com). No API key, no cost, works offline.

## It is separate from the voice on purpose

```
Verbatim mode (trusted)        Assistant mode (optional, this layer)
app/kachin_tts.py              llm/ollama_client.py
  text you wrote  -> audio        a request -> grounded local LLM -> draft text
  no LLM involved                 draft still needs native-speaker review
```

The text-to-speech core **never calls a language model**. It reads exactly
what it is given. This layer is only for the separate task of *drafting*
Kachin, and its output is always marked for review. For a theological
college, demonstrate verbatim mode for anything that must be exact; use the
assistant only as a drafting aid.

## Why local, and why honest about it

- **Free & offline.** A community project should not depend on a paid API
  or an internet connection. Ollama runs the model on your own machine.
- **Weak at Kachin -- and it says so.** General models barely know Kachin.
  This adapter grounds every request in the **verified** termbank entries
  and instructs the model to flag anything it is unsure of, instead of
  inventing confident nonsense. Grounding quality rises as native speakers
  verify more terms (`termbank/`).

## Use it

```bash
# one-time setup
#   install Ollama from https://ollama.com, then:
ollama pull llama3.2            # or qwen2.5, gemma2 -- any model you like

# point the adapter at your model (optional; defaults to llama3.2)
export OLLAMA_MODEL=llama3.2

python -m llm.ollama_client "Draft a short welcome for visitors"
```

If Ollama is not running, the adapter says so plainly and exits -- the
voice core is unaffected.

## Configuration

| Variable | Default | Meaning |
|---|---|---|
| `OLLAMA_MODEL` | `llama3.2` | any model you have pulled |
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama server address |

## Status

Phase 3 (grounded language layer) component. The `rag/` design describes
the retrieval strategy; this adapter is the local-LLM backend that design
plugs into. Ships now so the assistant path is free and offline from day
one.

