# Morse Toolkit

A simple GUI-based Morse code toolkit built with Python and PyQt5.

## Features

- Real-time Morse input via keyboard (Q = dot, E = dash)
- Text to Morse converter with Turkish character support
- Decode Morse from green-line images (SVG or similar)
- Generate oscilloscope-style SVG images from Morse code
- Main menu for selecting between tools

## Requirements

- Python 3.7+
- PyQt5
- numpy
- matplotlib
- pillow

See `requirements.txt` for exact versions.

## How to Run

1. Install dependencies:
`pip install -r requirements.txt`
2. Run the main menu:
`python main_menu.py`
3. ## File Structure

- `main_menu.py` — Launch menu
- `tra.py` — Real-time Morse input app
- `text2morse_window.py` — Text → Morse converter
- `svg2morse.py` — Morse from green signal image
- `morse2svg.py` — SVG from Morse code
- `morse_handler.py` — Handles key input logic
- `morse_dict.py` — Morse alphabet + Turkish replacements
