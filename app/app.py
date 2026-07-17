"""Kachin GPT -- Gradio interface.

Run from the repo root:

    python app/app.py

The model is warmed up at startup so the first click is fast. First
launch downloads the voice model (~145 MB); afterwards it works fully
offline.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Allow `python app/app.py` from the repo root.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import gradio as gr  # noqa: E402

from app.kachin_tts import SAMPLE_RATE, speak, warm_up  # noqa: E402

TITLE = "Kachin GPT -- Jinghpaw Text-to-Speech"

DESCRIPTION = """
Type a sentence in **Kachin (Jingpho)** and hear it spoken aloud.

**Verbatim by design:** this tool reads exactly the text you give it --
no words are generated or changed.

Voice model: [`facebook/mms-tts-kac`](https://huggingface.co/facebook/mms-tts-kac)
from Meta's Massively Multilingual Speech project -- one of the only neural
models ever trained on Kachin. This is Phase 1 of an open-source effort to
give the Kachin language a digital voice.
[Source & roadmap on GitHub](https://github.com/DanSengAwng/kachin-gpt).
"""

# Seed phrases -- common greetings, pending native-speaker review.
EXAMPLES = [
    "Chyeju kaba sai.",
    "Kaja ai i?",
]


def synthesize(text: str):
    """UI callback: text -> (sample_rate, waveform) for gr.Audio."""
    try:
        audio, rate = speak(text)
    except ValueError as exc:
        raise gr.Error(str(exc)) from exc
    return (rate, audio)


def build_demo() -> "gr.Blocks":
    with gr.Blocks(title=TITLE) as demo:
        gr.Markdown(f"# {TITLE}")
        gr.Markdown(DESCRIPTION)

        with gr.Row():
            with gr.Column():
                text_in = gr.Textbox(
                    label="Kachin text",
                    placeholder="Type Jinghpaw text here...",
                    lines=3,
                )
                speak_btn = gr.Button("Speak", variant="primary")
                gr.Examples(examples=EXAMPLES, inputs=text_in)
            with gr.Column():
                audio_out = gr.Audio(
                    label=f"Synthesized speech ({SAMPLE_RATE // 1000} kHz)",
                    type="numpy",
                )

        speak_btn.click(fn=synthesize, inputs=text_in, outputs=audio_out)
        text_in.submit(fn=synthesize, inputs=text_in, outputs=audio_out)

        gr.Markdown(
            "*Phase 1: verified base-model synthesis. Community fine-tuning "
            "and a termbank-grounded language layer are on the "
            "[roadmap](https://github.com/DanSengAwng/kachin-gpt#roadmap).*"
        )
    return demo


if __name__ == "__main__":
    print("Loading the Kachin voice model (first run downloads ~145 MB)...")
    warm_up()
    print("Model ready -- launching interface.")
    build_demo().launch()
