import sys as _sys, os
_sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # project root
_sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))                   # this dir

import random
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt
from dicts import MORSE_CODE_DICT
import cw_audio
from session_stats import log_session

# Resolve assets relative to the PROJECT ROOT (not this file's dir)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_MNEMONIC_DIR = os.path.join(_PROJECT_ROOT, "mnemonic_letter_images")

# States
STATE_WAITING  = "waiting"   # showing letter, waiting for user input
STATE_HINT     = "hint"      # wrong answer: mnemonic shown, answer hidden
STATE_REVEALED = "revealed"  # correct code shown, waiting for Enter → next


class MorseExerciseApp(QWidget):
    def __init__(self, return_callback=None):
        super().__init__()
        self.setWindowTitle("Morse Exercise")
        self.setGeometry(200, 100, 480, 600)
        self.return_callback = return_callback

        self.letters = [k for k in MORSE_CODE_DICT.keys() if k.isalpha()]
        self.current_letter = ""
        self.user_input = ""
        self.state = STATE_WAITING
        self._score_correct = 0
        self._score_total   = 0

        self._build_ui()
        self.next_letter()

    # ------------------------------------------------------------------ #
    #  UI construction                                                     #
    # ------------------------------------------------------------------ #
    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)

        # Instruction bar
        self.label_hint = QLabel("Type Morse:  Q = dot (·)   E = dash (—)   Enter = submit")
        self.label_hint.setAlignment(Qt.AlignCenter)
        self.label_hint.setFont(QFont("Arial", 10))
        self.label_hint.setStyleSheet("color: #888;")
        layout.addWidget(self.label_hint)

        # Big letter display
        self.label_letter = QLabel("")
        self.label_letter.setFont(QFont("Arial", 96, QFont.Bold))
        self.label_letter.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label_letter)

        # User's current input (dots & dashes)
        self.label_input = QLabel("")
        self.label_input.setFont(QFont("Courier", 28))
        self.label_input.setAlignment(Qt.AlignCenter)
        self.label_input.setStyleSheet("letter-spacing: 6px;")
        layout.addWidget(self.label_input)

        # Feedback line  (Correct / Wrong)
        self.label_feedback = QLabel("")
        self.label_feedback.setFont(QFont("Arial", 15, QFont.Bold))
        self.label_feedback.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label_feedback)

        # Mnemonic image
        self.label_image = QLabel("")
        self.label_image.setAlignment(Qt.AlignCenter)
        self.label_image.hide()
        layout.addWidget(self.label_image)

        # Mnemonic keyword + correct code shown below image
        self.label_mnemonic_text = QLabel("")
        self.label_mnemonic_text.setFont(QFont("Arial", 12))
        self.label_mnemonic_text.setAlignment(Qt.AlignCenter)
        self.label_mnemonic_text.hide()
        layout.addWidget(self.label_mnemonic_text)

        # Buttons row
        btn_layout = QHBoxLayout()
        self.next_button = QPushButton("Next  (Enter)")
        self.next_button.setFont(QFont("Arial", 11))
        self.next_button.setToolTip("Go to the next letter (also: press Enter)")
        self.next_button.clicked.connect(self._on_next_clicked)
        self.next_button.setEnabled(False)
        btn_layout.addWidget(self.next_button)

        self.skip_button = QPushButton("Skip")
        self.skip_button.setFont(QFont("Arial", 11))
        self.skip_button.setToolTip("Show the mnemonic hint without penalising your score")
        self.skip_button.clicked.connect(self._skip)
        btn_layout.addWidget(self.skip_button)

        # Audio mute toggle
        self.audio_button = QPushButton("Audio ON")
        self.audio_button.setFont(QFont("Arial", 11))
        self.audio_button.setToolTip("Toggle audio feedback on/off (sidetone beeps + answer playback)")
        self.audio_button.setCheckable(True)
        self.audio_button.setChecked(True)
        self.audio_button.toggled.connect(self._toggle_audio)
        btn_layout.addWidget(self.audio_button)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    # ------------------------------------------------------------------ #
    #  Flow control                                                        #
    # ------------------------------------------------------------------ #
    def _audio_enabled(self) -> bool:
        return cw_audio.is_available() and self.audio_button.isChecked()

    def _toggle_audio(self, checked: bool):
        self.audio_button.setText("Audio ON" if checked else "Audio OFF")
        if not checked:
            cw_audio.stop()

    def next_letter(self):
        self.current_letter = random.choice(self.letters)
        self.user_input = ""
        self.state = STATE_WAITING

        self.label_letter.setText(self.current_letter)
        self.label_input.setText("")
        self.label_feedback.setText("")
        self.label_feedback.setStyleSheet("")
        self.label_image.hide()
        self.label_mnemonic_text.hide()
        self.next_button.setEnabled(False)
        self.next_button.setText("Next  (Enter)")
        self.label_hint.setText("Type Morse:  Q = dot (·)   E = dash (—)   Enter = submit")
        self.setFocus()

    def _skip(self):
        """Jump straight to hint state without penalising."""
        if self.state == STATE_WAITING:
            self._go_to_hint(skipped=True)

    def _on_next_clicked(self):
        """Button click: act based on current state."""
        if self.state == STATE_HINT:
            self._reveal_answer()
        elif self.state == STATE_REVEALED:
            self.next_letter()

    def _go_to_hint(self, skipped: bool = False):
        """Show mnemonic image + keyword, but hide the correct code."""
        if not skipped:
            self._score_total += 1   # wrong answer counts as one attempt
        self.state = STATE_HINT
        if skipped:
            self.label_feedback.setText("Hint  —  can you guess the code?")
            self.label_feedback.setStyleSheet("color: #e8a838;")
        else:
            self.label_feedback.setText("Wrong!  —  here's a hint:")
            self.label_feedback.setStyleSheet("color: #f44336;")
        self._show_mnemonic(show_code=False)   # keyword only, no code yet
        self.next_button.setEnabled(True)
        self.label_hint.setText("Press Enter to reveal the answer.")
        self.next_button.setText("Reveal  (Enter)")

    def _reveal_answer(self):
        """Transition from HINT to REVEALED — show the correct code."""
        self.state = STATE_REVEALED
        expected = MORSE_CODE_DICT.get(self.current_letter, "")
        self.label_feedback.setText(
            f"{self.label_feedback.text().split('—')[0].strip()}  →  {expected}"
        )
        self._show_mnemonic(show_code=True)
        self.label_hint.setText("Press Enter or click Next for the next letter.")
        self.next_button.setText("Next  (Enter)")
        # Play the correct code so the user hears it
        if self._audio_enabled():
            cw_audio.play_morse(expected)

    def _correct(self):
        """Handle a correct answer — show mnemonic as positive reinforcement."""
        self._score_correct += 1
        self._score_total   += 1
        self.state = STATE_REVEALED
        expected = MORSE_CODE_DICT.get(self.current_letter, "")
        self.label_feedback.setText(f"Correct!   {expected}")
        self.label_feedback.setStyleSheet("color: #4caf50;")
        self._show_mnemonic(show_code=True)
        self.next_button.setEnabled(True)
        self.label_hint.setText("Press Enter or click Next for the next letter.")
        # Play the letter's Morse code so the user hears what it sounds like
        if self._audio_enabled():
            cw_audio.play_morse(expected)

    def _show_mnemonic(self, show_code: bool = True):
        """Load mnemonic image + keyword. Optionally append the correct code."""
        if not os.path.isdir(_MNEMONIC_DIR):
            return

        files = os.listdir(_MNEMONIC_DIR)
        match = next((f for f in files
                      if f.upper().startswith(self.current_letter.upper() + "_")), None)
        if match:
            path = os.path.join(_MNEMONIC_DIR, match)
            pixmap = QPixmap(path).scaledToWidth(220, Qt.SmoothTransformation)
            self.label_image.setPixmap(pixmap)
            self.label_image.show()

            keyword = os.path.splitext(match)[0].split("_", 1)[-1]
            if show_code:
                code = MORSE_CODE_DICT.get(self.current_letter, "")
                self.label_mnemonic_text.setText(f'  "{keyword}"   ->   {code}')
            else:
                self.label_mnemonic_text.setText(f'  "{keyword}"')
            self.label_mnemonic_text.show()

    # ------------------------------------------------------------------ #
    #  Keyboard handling                                                   #
    # ------------------------------------------------------------------ #
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
            return

        if self.state == STATE_REVEALED:
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                self.next_letter()
            return

        if self.state == STATE_HINT:
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                self._reveal_answer()
            return

        # STATE_WAITING
        if event.key() == Qt.Key_Q:
            self.user_input += "."
            if self._audio_enabled():
                cw_audio.play_dit()
        elif event.key() == Qt.Key_E:
            self.user_input += "-"
            if self._audio_enabled():
                cw_audio.play_dah()
        elif event.key() == Qt.Key_Backspace:
            self.user_input = self.user_input[:-1]
        elif event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self._check_input()
            return

        self.label_input.setText(self.user_input)

    def _check_input(self):
        if not self.user_input:
            return
        expected = MORSE_CODE_DICT.get(self.current_letter, "")
        if self.user_input == expected:
            self._correct()
        else:
            self._go_to_hint()

    # ------------------------------------------------------------------ #
    #  Window close                                                        #
    # ------------------------------------------------------------------ #
    def closeEvent(self, event):
        cw_audio.stop()
        if self._score_total > 0:
            log_session(
                "Morse Exercise",
                correct=self._score_correct,
                total=self._score_total
            )
        if self.return_callback:
            self.return_callback()
        event.accept()


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    win = MorseExerciseApp()
    win.show()
    sys.exit(app.exec_())
