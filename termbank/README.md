# Terminology Bank

A community-maintained vocabulary of Kachin (Jinghpaw) terms — greetings,
numbers, place names, and domain vocabulary (health, education, government)
— used to ground the language layer so proper nouns and key terms come from
curated data instead of model guesses.

## Schema (`termbank.csv`)

| Column | Meaning |
|---|---|
| `jinghpaw` | The Kachin term or phrase (Latin script) |
| `english` | English gloss |
| `domain` | Category: greetings, numbers, places, health, … |
| `notes` | Usage notes, register, alternatives |
| `verified` | `true` only after review by a native speaker |

## The honesty rule

**Every entry starts as `verified: false`.** An entry flips to `true` only
when a native Kachin speaker has reviewed it. The current seed entries are
common, well-attested items (greetings, numerals, major place names) added
to bootstrap development — they still await native-speaker sign-off, and
the pipeline treats them accordingly.

This is the community-in-the-loop design in miniature: the data model makes
"reviewed by a speaker" a first-class fact, not an assumption.

## Contributing

Native speakers: corrections and verifications are the single most valuable
contribution to this project. Open an issue or a PR that flips `verified`
to `true` with your name (or alias) in `notes` — or submit new entries in
any domain you know well.

