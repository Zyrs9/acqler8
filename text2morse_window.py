# text2morse_window.py
# Text → Morse converter window with proper closeEvent and ESC support.

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QLineEdit, QFrame
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from dicts import MORSE_CODE_DICT, normalize_turkish_characters
import cw_audio


class TextToMorseWindow(QWidget):
    def __init__(self, return_callback=None):
        super().__init__()
        self.return_callback = return_callback
        self.setWindowTitle("Text to Morse Converter")
        self.setGeometry(200, 150, 620, 420)
        self._build_ui()

    # ── UI ────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(18, 16, 18, 16)

        # Title
        title = QLabel("Text → Morse Converter")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: #444;")
        layout.addWidget(line)

        # Input
        layout.addWidget(QLabel("Enter text (supports Turkish characters):"))
        self.input_field = QLineEdit()
        self.input_field.setFont(QFont("Courier", 14))
        self.input_field.setPlaceholderText("Type here…")
        self.input_field.textChanged.connect(self._convert)
        layout.addWidget(self.input_field)

        # Output
        layout.addWidget(QLabel("Morse code output:"))
        self.output_field = QTextEdit()
        self.output_field.setReadOnly(True)
        self.output_field.setFont(QFont("Courier", 15))
        self.output_field.setStyleSheet("letter-spacing: 3px; line-height: 1.5;")
        layout.addWidget(self.output_field)

        # Buttons
        btn_row = QHBoxLayout()

        self.play_btn = QPushButton("▶  Play")
        self.play_btn.setFont(QFont("Arial", 11))
        self.play_btn.setToolTip("Play the Morse code as audio")
        self.play_btn.clicked.connect(self._play)
        btn_row.addWidget(self.play_btn)

        self.stop_btn = QPushButton("■  Stop")
        self.stop_btn.setFont(QFont("Arial", 11))
        self.stop_btn.setToolTip("Stop audio playback")
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

    # ── Logic ─────────────────────────────────────────────────────────────────
    def _convert(self):
        raw = self.input_field.text()
        normalized = normalize_turkish_characters(raw.upper())
        morse = []
        for ch in normalized:
            if ch == " ":
                morse.append("/")
            else:
                code = MORSE_CODE_DICT.get(ch, "?")
                morse.append(code)
        self.output_field.setPlainText(" ".join(morse))

    def _play(self):
        morse = self.output_field.toPlainText().strip()
        if morse and cw_audio.is_available():
            cw_audio.play_morse(morse)

    # ── ESC / close ───────────────────────────────────────────────────────────
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
