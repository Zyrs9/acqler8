# wpm_trainer.py
# WPM Speed Trainer — plays random Morse audio and scores the user's decode.
# Supports Farnsworth spacing mode.

import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))  # root
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))                    # training/

import random
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QComboBox, QCheckBox, QSpinBox, QFrame, QSlider
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from dicts import MORSE_CODE_DICT
import cw_audio
from session_stats import log_session

# ── Word banks ────────────────────────────────────────────────────────────────
COMMON_WORDS = [
    "THE", "AND", "FOR", "ARE", "BUT", "NOT", "YOU", "ALL",
    "CAN", "HER", "WAS", "ONE", "OUR", "OUT", "DAY", "GET",
    "HAS", "HIM", "HOW", "MAN", "NEW", "NOW", "OLD", "SEE",
    "TWO", "WAY", "WHO", "BOY", "DID", "ITS", "LET", "PUT",
    "SAY", "TOO", "USE",
]
CW_WORDS = [
    "CQ", "DE", "RST", "QTH", "QRZ", "QSO", "QRM", "QRN",
    "73", "88", "K", "AR", "SK", "BK", "TNX", "UR", "ES",
    "AGN", "PSE", "RPT", "HR", "HW", "FB", "NR", "OM",
]

# ── Callsign generator ────────────────────────────────────────────────────────
_PREFIXES = ["W", "K", "N", "AA", "VK", "G", "F", "DL", "JA", "HS", "TA"]
_LETTERS  = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
_DIGITS   = "0123456789"

def _random_callsign() -> str:
    prefix = random.choice(_PREFIXES)
    digit  = random.choice(_DIGITS)
    suffix = "".join(random.choices(_LETTERS, k=random.randint(2, 3)))
    return f"{prefix}{digit}{suffix}"


def _to_morse(text: str) -> str:
    parts = []
    for ch in text.upper():
        if ch == " ":
            parts.append("/")
        elif ch in MORSE_CODE_DICT:
            parts.append(MORSE_CODE_DICT[ch])
    return " ".join(parts)


# ── Audio worker ──────────────────────────────────────────────────────────────
class AudioWorker(QThread):
    finished = pyqtSignal()

    def __init__(self, morse: str, wpm: int, farnsworth: bool):
        super().__init__()
        self.morse = morse
        self.wpm = wpm
        self.farnsworth = farnsworth

    def run(self):
        fw = max(5, self.wpm - 5) if self.farnsworth else 0
        cw_audio.play_morse(self.morse, wpm=self.wpm, farnsworth_wpm=fw, blocking=True)
        self.finished.emit()


# ── Main widget ───────────────────────────────────────────────────────────────
class WpmTrainer(QWidget):
    def __init__(self, return_callback=None):
        super().__init__()
        self.return_callback = return_callback
        self.setWindowTitle("WPM Speed Trainer")
        self.setGeometry(200, 100, 520, 480)

        self._current_text = ""
        self._current_morse = ""
        self._score_correct = 0
        self._score_total   = 0
        self._worker: AudioWorker | None = None

        self._build_ui()

    # ── UI ──────────────────────────────────────────────────────────────────
    def _build_ui(self):
        main = QVBoxLayout()
        main.setSpacing(10)

        # ── Settings row ──
        settings = QHBoxLayout()

        settings.addWidget(QLabel("WPM:"))
        self.wpm_spin = QSpinBox()
        self.wpm_spin.setRange(5, 40)
        self.wpm_spin.setValue(15)
        self.wpm_spin.setFixedWidth(60)
        settings.addWidget(self.wpm_spin)

        self.farnsworth_cb = QCheckBox("Farnsworth")
        self.farnsworth_cb.setToolTip(
            "Letters sent at selected WPM; extra gaps between letters/words to allow thinking time."
        )
        settings.addWidget(self.farnsworth_cb)

        settings.addWidget(QLabel("  Mode:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Letters", "Common Words", "CW Abbreviations", "Callsigns"])
        settings.addWidget(self.mode_combo)

        settings.addStretch()
        main.addLayout(settings)

        # ── Noise row ──
        noise_row = QHBoxLayout()
        noise_row.addWidget(QLabel("Noise (SNR dB, 0=off):"))
        self.noise_slider = QSlider(Qt.Horizontal)
        self.noise_slider.setRange(0, 30)
        self.noise_slider.setValue(0)
        self.noise_slider.setTickInterval(5)
        self.noise_slider.setFixedWidth(120)
        self.noise_label = QLabel("0")
        self.noise_slider.valueChanged.connect(
            lambda v: self.noise_label.setText(str(v))
        )
        noise_row.addWidget(self.noise_slider)
        noise_row.addWidget(self.noise_label)

        noise_row.addSpacing(16)
        noise_row.addWidget(QLabel("QRM Hz (0=off):"))
        self.qrm_spin = QSpinBox()
        self.qrm_spin.setRange(0, 2000)
        self.qrm_spin.setSingleStep(50)
        self.qrm_spin.setValue(0)
        self.qrm_spin.setFixedWidth(75)
        noise_row.addWidget(self.qrm_spin)
        noise_row.addStretch()
        main.addLayout(noise_row)

        # ── Divider ──
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: #555;")
        main.addWidget(line)

        # ── Status / instruction ──
        self.label_status = QLabel("Press ▶ Play to hear a Morse sequence, then type what you heard.")
        self.label_status.setAlignment(Qt.AlignCenter)
        self.label_status.setWordWrap(True)
        self.label_status.setFont(QFont("Arial", 11))
        main.addWidget(self.label_status)

        # ── Morse display (shown after answer checked) ──
        self.label_morse = QLabel("")
        self.label_morse.setFont(QFont("Courier", 16))
        self.label_morse.setAlignment(Qt.AlignCenter)
        self.label_morse.setStyleSheet("letter-spacing: 4px; color: #aaa;")
        main.addWidget(self.label_morse)

        # ── Answer label ──
        self.label_answer = QLabel("")
        self.label_answer.setFont(QFont("Arial", 30, QFont.Bold))
        self.label_answer.setAlignment(Qt.AlignCenter)
        main.addWidget(self.label_answer)

        # ── User input ──
        self.input_field = QLineEdit()
        self.input_field.setFont(QFont("Arial", 18))
        self.input_field.setAlignment(Qt.AlignCenter)
        self.input_field.setPlaceholderText("Type what you heard…")
        self.input_field.returnPressed.connect(self._check_answer)
        self.input_field.setEnabled(False)
        main.addWidget(self.input_field)

        # ── Feedback ──
        self.label_feedback = QLabel("")
        self.label_feedback.setFont(QFont("Arial", 14, QFont.Bold))
        self.label_feedback.setAlignment(Qt.AlignCenter)
        main.addWidget(self.label_feedback)

        # ── Score ──
        self.label_score = QLabel("Score: —")
        self.label_score.setFont(QFont("Arial", 11))
        self.label_score.setAlignment(Qt.AlignCenter)
        self.label_score.setStyleSheet("color: #aaa;")
        main.addWidget(self.label_score)

        # ── Buttons ──
        btns = QHBoxLayout()
        self.play_button = QPushButton("Play")
        self.play_button.setFont(QFont("Arial", 12))
        self.play_button.setToolTip("Play the current Morse sequence (also: press Enter)")
        self.play_button.clicked.connect(self._play)
        btns.addWidget(self.play_button)

        self.replay_button = QPushButton("Replay")
        self.replay_button.setFont(QFont("Arial", 12))
        self.replay_button.setToolTip("Replay the last Morse sequence")
        self.replay_button.clicked.connect(self._replay)
        self.replay_button.setEnabled(False)
        btns.addWidget(self.replay_button)

        self.check_button = QPushButton("Check")
        self.check_button.setFont(QFont("Arial", 12))
        self.check_button.setToolTip("Submit your typed answer for checking (also: press Enter)")
        self.check_button.clicked.connect(self._check_answer)
        self.check_button.setEnabled(False)
        btns.addWidget(self.check_button)

        self.skip_button = QPushButton("Skip")
        self.skip_button.setFont(QFont("Arial", 12))
        self.skip_button.setToolTip("Skip this sequence and reveal the answer")
        self.skip_button.clicked.connect(self._skip)
        self.skip_button.setEnabled(False)
        btns.addWidget(self.skip_button)

        main.addLayout(btns)
        self.setLayout(main)

    # ── Logic ────────────────────────────────────────────────────────────────
    def _pick_text(self) -> str:
        mode = self.mode_combo.currentText()
        if mode == "Letters":
            return random.choice([k for k in MORSE_CODE_DICT if k.isalpha()])
        elif mode == "Common Words":
            return random.choice(COMMON_WORDS)
        elif mode == "CW Abbreviations":
            return random.choice(CW_WORDS)
        else:
            return _random_callsign()

    def _play(self):
        self._current_text  = self._pick_text()
        self._current_morse = _to_morse(self._current_text)
        self._start_playback(new=True)

    def _replay(self):
        if self._current_morse:
            self._start_playback(new=False)

    def _start_playback(self, new: bool):
        cw_audio.stop()

        if new:
            self.label_answer.setText("")
            self.label_morse.setText("")
            self.label_feedback.setText("")
            self.input_field.clear()

        self.input_field.setEnabled(False)
        self.play_button.setEnabled(False)
        self.check_button.setEnabled(False)
        self.replay_button.setEnabled(False)
        self.skip_button.setEnabled(False)
        self.label_status.setText("Playing...")

        # Apply noise settings before building audio
        cw_audio.set_noise(
            noise_db=float(self.noise_slider.value()),
            qrm_freq=float(self.qrm_spin.value())
        )

        fw = max(5, self.wpm_spin.value() - 5) if self.farnsworth_cb.isChecked() else 0
        self._worker = AudioWorker(self._current_morse, self.wpm_spin.value(), fw > 0)
        self._worker.farnsworth = fw > 0
        self._worker.finished.connect(self._on_playback_done)
        self._worker.start()

    def _on_playback_done(self):
        self.input_field.setEnabled(True)
        self.play_button.setEnabled(True)
        self.check_button.setEnabled(True)
        self.replay_button.setEnabled(True)
        self.skip_button.setEnabled(True)
        self.input_field.setFocus()
        self.label_status.setText("Type what you heard, then press Check or Enter.")

    def _check_answer(self):
        if not self._current_text:
            return
        user = self.input_field.text().strip().upper()
        correct = self._current_text.upper()
        self._score_total += 1

        if user == correct:
            self._score_correct += 1
            self.label_feedback.setText(f"Correct!")
            self.label_feedback.setStyleSheet("color: #4caf50;")
        else:
            self.label_feedback.setText(f"Wrong!")
            self.label_feedback.setStyleSheet("color: #f44336;")

        self.label_answer.setText(correct)
        self.label_morse.setText(self._current_morse)
        pct = round(self._score_correct / self._score_total * 100)
        self.label_score.setText(
            f"Score: {self._score_correct}/{self._score_total}  ({pct}%)"
        )
        self.input_field.setEnabled(False)
        self.check_button.setEnabled(False)
        self.skip_button.setEnabled(False)

    def _skip(self):
        self._score_total += 1
        self.label_answer.setText(self._current_text.upper())
        self.label_morse.setText(self._current_morse)
        self.label_feedback.setText("Skipped")
        self.label_feedback.setStyleSheet("color: #e8a838;")
        pct = round(self._score_correct / self._score_total * 100)
        self.label_score.setText(
            f"Score: {self._score_correct}/{self._score_total}  ({pct}%)"
        )
        self.input_field.setEnabled(False)
        self.check_button.setEnabled(False)
        self.skip_button.setEnabled(False)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)

    def closeEvent(self, event):
        cw_audio.stop()
        cw_audio.set_noise(0.0, 0.0)   # reset noise on exit
        if self._score_total > 0:
            log_session(
                "WPM Trainer",
                correct=self._score_correct,
                total=self._score_total,
                wpm=self.wpm_spin.value()
            )
        if self.return_callback:
            self.return_callback()
        event.accept()


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    win = WpmTrainer()
    win.show()
    sys.exit(app.exec_())
