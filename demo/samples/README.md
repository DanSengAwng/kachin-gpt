# Audio Samples

Synthesized by this repo's pipeline (`app/kachin_tts.py`, model
`facebook/mms-tts-kac`, 16 kHz mono WAV).

| File | Kachin text | English gloss |
|---|---|---|
| `chyeju_kaba_sai.wav` | Chyeju kaba sai. | Thank you very much. |
| `kaja_ai_i.wav` | Kaja ai i? | How are you? |
| `numbers_1_to_5.wav` | Langai. Lahkawng. Masum. Mali. Manga. | One. Two. Three. Four. Five. |

Phrases are common greetings/numerals from the seed termbank
(pending native-speaker review — see `termbank/README.md`).

Regenerate any sample:

```python
from app.kachin_tts import save_wav
save_wav("Chyeju kaba sai.", "demo/samples/chyeju_kaba_sai.wav")
```

