"""Optional local-LLM assistant layer for Kachin GPT.

This package is SEPARATE from the verbatim text-to-speech core. The core
(`app/kachin_tts.py`) never calls a language model -- it reads exactly the
text it is given. This layer adds an optional "assistant" mode that can
draft or explain Kachin, grounded by the terminology bank, using a free
local model served by Ollama. Nothing here runs unless you start Ollama
yourself.
"""

