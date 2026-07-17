# Recording Kit

Everything a partner organization (a college, church, or community group)
needs to run a **voice recording session** whose output feeds directly into
the fine-tuning pipeline. One afternoon with 3 speakers produces the first
usable corpus.

## The afternoon workflow

1. **Prepare (before the day)**
   - Print `recording-script.md` (one copy per speaker) and
     `consent-form.md` (translated -- see below).
   - Choose a quiet room: soft furnishings, door closed, phones on silent.
   - Any modern phone's voice recorder works. Set it to the highest
     quality available; we downsample to 16 kHz later.

2. **Record (per speaker, ~45 minutes)**
   - Sign the consent form first. No signature, no recording.
   - Phone flat on the table, about 30 cm from the speaker.
   - The speaker reads each script item **twice**, pausing between takes.
   - Mistake? Just pause and read the item again -- do not stop the
     recording.

3. **Validate (same day)**
   - Convert phone files to WAV:
     `ffmpeg -i clip.m4a -ar 16000 -ac 1 clip.wav`
   - Run the validator:
     `python sft/recording-kit/check_recording.py recordings/*.wav`
   - Re-record anything marked FAIL while everyone is still in the room.

4. **Package**
   - File naming: `spk01_R001.wav` (speaker ID + script item ID).
   - Fill one metadata row per file (see below), zip, done.

## Metadata (one row per clip -- keep it a simple CSV)

| Column | Example | Notes |
|---|---|---|
| `file` | spk01_R001.wav | |
| `speaker_id` | spk01 | never the person's name |
| `text_id` | R001 | from the recording script |
| `age_range` | 40-60 | ranges, not exact ages |
| `gender` | f | |
| `region` | Myitkyina | dialect area, self-described |
| `consent` | yes | consent form on file |

## Privacy defaults

Speaker identities stay out of filenames and metadata. The consent form
records each contributor's attribution choice -- credited by name, by
alias, or anonymous -- and that choice is honored everywhere the data
appears.

## What we still need from native speakers (data gaps)

- Verification of the seed termbank (`termbank/termbank.csv`)
- Spoken forms of numerals beyond five, dates, and times -- needed before
  a number-reading feature can be built honestly
- Everyday sentences for Block B of the recording script (the script
  deliberately ships with empty slots rather than machine-written Kachin)

