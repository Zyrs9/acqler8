import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))  # root
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))                    # training/

import random
import time
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QEvent
from dicts import MORSE_CODE_DICT
from wpm_trainer import COMMON_WORDS, CW_WORDS, _random_callsign
import cw_audio
from session_stats import log_session

# ── Helpers ───────────────────────────────────────────────────────────────────
def _to_morse(text: str) -> str:
    parts = []
    for ch in text.upper():
        if ch == " ":
            parts.append("/")
        elif ch in MORSE_CODE_DICT:
            parts.append(MORSE_CODE_DICT[ch])
    return " ".join(parts)


def _char_count(text: str) -> int:
    """Standard Morse WPM: 5 chars = 1 word."""
    return len(text.replace(" ", ""))


def _calc_wpm(chars: int, elapsed_sec: float) -> float:
    if elapsed_sec <= 0:
        return 0.0
    words = chars / 5.0
    minutes = elapsed_sec / 60.0
    return round(words / minutes, 1)


# ── Main widget ───────────────────────────────────────────────────────────────
class SendPractice(QWidget):
    def __init__(self, return_callback=None):
        super().__init__()
        self.return_callback = return_callback
        self.setWindowTitle("Send Practice")
        self.setGeometry(200, 100, 500, 550)

        # Prevent Qt from using Tab for focus cycling inside this widget
        self.setFocusPolicy(Qt.StrongFocus)

        self._target_text  = ""
        self._target_morse = ""
        self._user_input   = ""
        self._start_time   = None
        self._awaiting_next = False

        self._score_total  = 0
        self._score_correct = 0

        self._build_ui()
        self._next_word()
        # Install event filter on the application so we catch Tab
        # before Qt's focus system swallows it
        QApplication.instance().installEventFilter(self)

    # ── UI ──────────────────────────────────────────────────────────────────
    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)

        # instructions
        hint = QLabel("Encode the word below using  Q = dot (·)   E = dash (—)\n"
                       "SPACE = next letter   TAB = next word   ENTER = submit")
        hint.setAlignment(Qt.AlignCenter)
        hint.setFont(QFont("Arial", 10))
        hint.setStyleSheet("color: #888;")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: #444;")
        layout.addWidget(line)

        # Word to encode
        layout.addWidget(QLabel("Encode this:"))
        self.label_target = QLabel("")
        self.label_target.setFont(QFont("Arial", 56, QFont.Bold))
        self.label_target.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label_target)

        # Expected Morse (hidden until submitted)
        self.label_expected_morse = QLabel("")
        self.label_expected_morse.setFont(QFont("Courier", 13))
        self.label_expected_morse.setAlignment(Qt.AlignCenter)
        self.label_expected_morse.setStyleSheet("color: #666;")
        layout.addWidget(self.label_expected_morse)

        # User's current Morse input
        layout.addWidget(QLabel("Your input:"))
        self.label_user_input = QLabel("")
        self.label_user_input.setFont(QFont("Courier", 18))
        self.label_user_input.setAlignment(Qt.AlignCenter)
        self.label_user_input.setStyleSheet("letter-spacing: 4px;")
        layout.addWidget(self.label_user_input)

        # Feedback
        self.label_feedback = QLabel("")
        self.label_feedback.setFont(QFont("Arial", 14, QFont.Bold))
        self.label_feedback.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label_feedback)

        # WPM result
        self.label_wpm = QLabel("")
        self.label_wpm.setFont(QFont("Arial", 22, QFont.Bold))
        self.label_wpm.setAlignment(Qt.AlignCenter)
        self.label_wpm.setStyleSheet("color: #4caf50;")
        layout.addWidget(self.label_wpm)

        # Score
        self.label_score = QLabel("Score: —")
        self.label_score.setFont(QFont("Arial", 11))
        self.label_score.setAlignment(Qt.AlignCenter)
        self.label_score.setStyleSheet("color: #aaa;")
        layout.addWidget(self.label_score)

        # Buttons
        btns = QHBoxLayout()
        self.next_button = QPushButton("Next  (Enter after submitted)")
        self.next_button.setFont(QFont("Arial", 11))
        self.next_button.setToolTip("Move to the next word (also: press Enter after submitting)")
        self.next_button.clicked.connect(self._next_word)
        self.next_button.setEnabled(False)
        btns.addWidget(self.next_button)

        self.skip_button = QPushButton("Skip")
        self.skip_button.setFont(QFont("Arial", 11))
        self.skip_button.setToolTip("Skip this word and reveal the correct Morse code")
        self.skip_button.clicked.connect(self._skip)
        btns.addWidget(self.skip_button)

        layout.addLayout(btns)
        self.setLayout(layout)

    # ── Logic ────────────────────────────────────────────────────────────────
    def _next_word(self):
        pool = COMMON_WORDS + CW_WORDS
        self._target_text  = random.choice(pool)
        self._target_morse = _to_morse(self._target_text)
        self._user_input   = ""
        self._start_time   = None
        self._awaiting_next = False

        self.label_target.setText(self._target_text)
        self.label_expected_morse.setText("")
        self.label_user_input.setText("")
        self.label_feedback.setText("")
        self.label_wpm.setText("")
        self.next_button.setEnabled(False)
        self.skip_button.setEnabled(True)
        self.setFocus()          # ensure this widget receives key events

    # ── Event filter: catches ALL keys regardless of focus ───────────────────
    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress and self.isVisible():
            self._handle_key(event.key())
            # Always consume so Qt doesn't do focus-cycling or other side-effects
            if event.key() in (Qt.Key_Tab, Qt.Key_Escape, Qt.Key_Q, Qt.Key_E,
                               Qt.Key_Space, Qt.Key_Backspace,
                               Qt.Key_Return, Qt.Key_Enter):
                return True
        return super().eventFilter(obj, event)

    def _handle_key(self, key):
        if key == Qt.Key_Escape:
            self.close()
            return

        if self._awaiting_next:
            if key in (Qt.Key_Return, Qt.Key_Enter):
                self.skip_button.setEnabled(True)
                self._next_word()
            return

        # Start timer on first real keypress
        if self._start_time is None and key in (Qt.Key_Q, Qt.Key_E):
            self._start_time = time.time()

        if key == Qt.Key_Q:
            self._user_input += "."
            cw_audio.play_dit()
        elif key == Qt.Key_E:
            self._user_input += "-"
            cw_audio.play_dah()
        elif key == Qt.Key_Backspace:
            self._user_input = self._user_input[:-1]
        elif key == Qt.Key_Space:
            self._user_input += " "      # inter-letter separator
        elif key == Qt.Key_Tab:
            self._user_input += " / "    # inter-word separator
        elif key in (Qt.Key_Return, Qt.Key_Enter):
            if self._user_input.strip():
                self._submit()
            return

        self.label_user_input.setText(self._user_input)


    def _skip(self):
        self._score_total += 1
        self._show_answer(correct=False, skipped=True)

    def _show_answer(self, correct: bool, skipped: bool = False, wpm: float = 0):
        self._awaiting_next = True
        self.label_expected_morse.setText(self._target_morse)
        self.next_button.setEnabled(True)
        self.skip_button.setEnabled(False)

        if skipped:
            self.label_feedback.setText("Skipped")
            self.label_feedback.setStyleSheet("color: #e8a838;")
            self.label_wpm.setText("")
        elif correct:
            self.label_feedback.setText("Correct!")
            self.label_feedback.setStyleSheet("color: #4caf50;")
            self.label_wpm.setText(f"{wpm} WPM")
        else:
            self.label_feedback.setText("Wrong!")
            self.label_feedback.setStyleSheet("color: #f44336;")
            self.label_wpm.setText("")

        pct = round(self._score_correct / self._score_total * 100) if self._score_total else 0
        self.label_score.setText(
            f"Score: {self._score_correct}/{self._score_total}  ({pct}%)"
        )

    def _submit(self):
        elapsed = time.time() - self._start_time if self._start_time else 0
        user_morse = self._user_input.strip()
        correct = (user_morse == self._target_morse.strip())
        self._score_total += 1
        if correct:
            self._score_correct += 1
        wpm = _calc_wpm(_char_count(self._target_text), elapsed)
        # Play back the correct Morse so user can hear it
        if cw_audio.is_available():
            cw_audio.play_morse(self._target_morse)
        self._show_answer(correct=correct, wpm=wpm if correct else 0)

    # keyPressEvent intentionally omitted:
    # all key handling happens in eventFilter (app-level) so it
    # fires regardless of which child widget currently has focus.

    def closeEvent(self, event):
        QApplication.instance().removeEventFilter(self)
        cw_audio.stop()
        if self._score_total > 0:
            log_session(
                "Send Practice",
                correct=self._score_correct,
                total=self._score_total,
                wpm=0.0
            )
        if self.return_callback:
            self.return_callback()
        event.accept()


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    win = SendPractice()
    win.show()
    sys.exit(app.exec_())
