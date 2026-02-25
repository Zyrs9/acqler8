# Morse / CW Toolkit

> A pet project for learning Morse code / Telephony. Nothing fancy, but it works pretty well. Might work on it more in the future. For now, I just plan to add more exercises such as regulations, past exam questions as well as features like better QRM simulation, easy to come across lines for radio operators, etc.

---

## What it does

- **Morse Exercise** — flashes a letter, you tap Q (dot) or E (dash) to identify it. Shows a mnemonic image to help you remember.
- **WPM Speed Trainer** — plays random Morse audio at a set WPM, you type what you hear. Tracks accuracy and score.
- **Send Practice** — shows a word, you encode it with Q/E. Times you and calculates your sending WPM.
- **Phonetic Alphabet Drill** — drills NATO phonetics both ways (letter→word and word→letter).
- **Real-Time Morse Input** — type Q/E freely and watch it decode live as you type.
- **Text → Morse Converter** — paste in any text (Turkish characters supported) and hear or see the Morse output.
- **Decode Morse from Image** — reads green-bar Morse signal images and pulls out the code.
- **Generate SVG from Morse** — renders a Morse code waveform as an SVG image.
- **Q-Code Reference** — searchable table of Q-codes, prosigns, and common CW abbreviations.
- **Session Stats** — keeps a log of your practice sessions (accuracy + WPM) so you can see progress over time.

---

## Controls (in most training tools)

| Key | Action |
|-----|--------|
| Q | Dot (·) |
| E | Dash (—) |
| Space | Next letter separator |
| Tab | Next word separator |
| Enter | Submit / confirm |
| Backspace | Delete last element |
| ESC | Back to main menu |

---

## Running it

```bash
pip install -r requirements.txt
python main_menu.py
```

Needs Python 3.8+, PyQt5, numpy, sounddevice, and pillow. Everything else is stdlib.

---

## Files

| File | What it is |
|------|------------|
| `main_menu.py` | Entry point / launcher |
| `cw_audio.py` | Morse audio engine (numpy + sounddevice) |
| `morse_exercise.py` | Letter recognition trainer |
| `wpm_trainer.py` | Speed drill |
| `send_practice.py` | Sending practice |
| `phonetic_drill.py` | NATO phonetics drill |
| `tra.py` | Real-time Morse input |
| `text2morse_window.py` | Text → Morse converter |
| `svg2morse.py` | Image → Morse decoder |
| `morse2svg.py` | Morse → SVG generator (via [aalex954](https://github.com/aalex954)) |
| `qcode_reference.py` | Q-code reference viewer |
| `session_stats.py` | Session logging + stats viewer |
| `morse_handler.py` | Key input → Morse symbol logic |
| `dicts.py` | Morse alphabet, Turkish mappings, NATO phonetics, Q-codes |

---

*Made for fun while helping my friend study*
