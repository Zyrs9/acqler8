# svg2morse.py
# Decode Morse code from an image by reading green signal bars.
# Runs as a proper QWidget so it returns to the main menu on close.

from PIL import Image
import numpy as np
from itertools import groupby
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QFrame, QFileDialog
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import cw_audio


def _extract_morse(image_path: str) -> str:
    """Read green-bar Morse signal from an image file."""
    rgb_image = Image.open(image_path).convert("RGB")
    rgb_array = np.array(rgb_image)

    green_mask = (
        (rgb_array[:, :, 1] > 200) &
        (rgb_array[:, :, 0] < 100) &
        (rgb_array[:, :, 2] < 100)
    )

    green_signal_1d = green_mask.any(axis=0).astype(int)
    runs = [(val, sum(1 for _ in group)) for val, group in groupby(green_signal_1d)]

    signal_lengths = [length for val, length in runs if val == 1]
    space_lengths  = [length for val, length in runs if val == 0]

    if not signal_lengths or not space_lengths:
        return "No Morse signal detected."

    min_dot               = min(signal_lengths)
    dot_dash_threshold    = min_dot * 2
    min_space             = min(space_lengths)
    letter_space_thr      = min_space * 3
    word_space_thr        = min_space * 6

    morse = ""
    for val, length in runs:
        if val == 1:
            morse += "." if length < dot_dash_threshold else "-"
        else:
            if length >= word_space_thr:
                morse += "   "
            elif length >= letter_space_thr:
                morse += " "
    return morse


class Svg2MorseWindow(QWidget):
    """Widget-based image→Morse decoder so it returns to main menu on close."""

    def __init__(self, return_callback=None):
        super().__init__()
        self.return_callback = return_callback
        self.setWindowTitle("Decode Morse from Image")
        self.setGeometry(200, 150, 620, 400)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(18, 16, 18, 16)

        title = QLabel("Image → Morse Decoder")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title)

        hint = QLabel("Reads green signal bars from PNG/JPG/BMP/WEBP images.")
        hint.setFont(QFont("Arial", 10))
        hint.setStyleSheet("color: #888;")
        layout.addWidget(hint)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: #444;")
        layout.addWidget(line)

        self.label_file = QLabel("No file selected.")
        self.label_file.setFont(QFont("Arial", 10))
        self.label_file.setStyleSheet("color: #aaa;")
        layout.addWidget(self.label_file)

        layout.addWidget(QLabel("Decoded Morse:"))
        self.output_field = QTextEdit()
        self.output_field.setReadOnly(True)
        self.output_field.setFont(QFont("Courier", 15))
        self.output_field.setStyleSheet("letter-spacing: 3px;")
        layout.addWidget(self.output_field)

        btn_row = QHBoxLayout()

        open_btn = QPushButton("📂  Open Image…")
        open_btn.setFont(QFont("Arial", 11))
        open_btn.setToolTip("Choose an image file to decode")
        open_btn.clicked.connect(self._open_file)
        btn_row.addWidget(open_btn)

        self.play_btn = QPushButton("▶  Play")
        self.play_btn.setFont(QFont("Arial", 11))
        self.play_btn.setToolTip("Play the decoded Morse as audio")
        self.play_btn.setEnabled(False)
        self.play_btn.clicked.connect(self._play)
        btn_row.addWidget(self.play_btn)

        self.stop_btn = QPushButton("■  Stop")
        self.stop_btn.setFont(QFont("Arial", 11))
        self.stop_btn.clicked.connect(cw_audio.stop)
        btn_row.addWidget(self.stop_btn)

        btn_row.addStretch()

        back_btn = QPushButton("← Back to Menu")
        back_btn.setFont(QFont("Arial", 11))
        back_btn.setToolTip("Return to the main menu  (ESC)")
        back_btn.clicked.connect(self.close)
        btn_row.addWidget(back_btn)

        layout.addLayout(btn_row)
        self.setLayout(layout)

    def _open_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "",
            "Images (*.png *.jpg *.bmp *.webp)"
        )
        if not path:
            return
        self.label_file.setText(path)
        try:
            morse = _extract_morse(path)
        except Exception as e:
            morse = f"Error: {e}"
        self.output_field.setPlainText(morse)
        self.play_btn.setEnabled(bool(morse.strip()))

    def _play(self):
        morse = self.output_field.toPlainText().strip()
        if morse and cw_audio.is_available():
            cw_audio.play_morse(morse)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)

    def closeEvent(self, event):
        cw_audio.stop()
        if self.return_callback:
            self.return_callback()
        event.accept()


# Keep the old function name for any external callers — no longer needed
# (main_menu now uses Svg2MorseWindow directly)
def run_svg2morse_gui():
    """Legacy stub — replaced by Svg2MorseWindow."""
    pass
