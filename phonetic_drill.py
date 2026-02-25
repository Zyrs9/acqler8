# phonetic_drill.py
# Phonetic Alphabet Drill — flash a letter, user types the NATO word (or reverse).

import random
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QComboBox, QFrame
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from dicts import NATO_PHONETIC_DICT
from session_stats import log_session

# Reverse: word -> letter
PHONETIC_TO_LETTER = {v.upper(): k for k, v in NATO_PHONETIC_DICT.items()}


class PhoneticDrill(QWidget):
    def __init__(self, return_callback=None):
        super().__init__()
        self.return_callback = return_callback
        self.setWindowTitle("Phonetic Alphabet Drill")
        self.setGeometry(200, 150, 440, 440)

        self._score_correct = 0
        self._score_total   = 0
        self._current_key   = ""
        self._awaiting_next = False

        self._build_ui()
        self._next()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)

        # Mode selector
        mode_row = QHBoxLayout()
        mode_row.addWidget(QLabel("Mode:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems([
            "Letter → NATO word",
            "NATO word → Letter",
        ])
        self.mode_combo.currentIndexChanged.connect(self._mode_changed)
        mode_row.addWidget(self.mode_combo)
        mode_row.addStretch()
        layout.addLayout(mode_row)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: #444;")
        layout.addWidget(line)

        # Prompt label (big)
        self.label_prompt_desc = QLabel("Type the NATO word:")
        self.label_prompt_desc.setFont(QFont("Arial", 11))
        self.label_prompt_desc.setStyleSheet("color: #888;")
        self.label_prompt_desc.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label_prompt_desc)

        self.label_prompt = QLabel("")
        self.label_prompt.setFont(QFont("Arial", 72, QFont.Bold))
        self.label_prompt.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label_prompt)

        # Input
        self.input_field = QLineEdit()
        self.input_field.setFont(QFont("Arial", 18))
        self.input_field.setAlignment(Qt.AlignCenter)
        self.input_field.setPlaceholderText("Your answer…")
        self.input_field.returnPressed.connect(self._check)
        layout.addWidget(self.input_field)

        # Feedback
        self.label_feedback = QLabel("")
        self.label_feedback.setFont(QFont("Arial", 14, QFont.Bold))
        self.label_feedback.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label_feedback)

        # Score
        self.label_score = QLabel("Score: —")
        self.label_score.setFont(QFont("Arial", 11))
        self.label_score.setAlignment(Qt.AlignCenter)
        self.label_score.setStyleSheet("color: #aaa;")
        layout.addWidget(self.label_score)

        # Buttons
        btn_row = QHBoxLayout()
        self.check_btn = QPushButton("Check")
        self.check_btn.setToolTip("Check your answer (also: press Enter)")
        self.check_btn.clicked.connect(self._check)
        btn_row.addWidget(self.check_btn)

        self.next_btn = QPushButton("Next")
        self.next_btn.setToolTip("Move to the next question (also: press Enter after answering)")
        self.next_btn.setEnabled(False)
        self.next_btn.clicked.connect(self._next)
        btn_row.addWidget(self.next_btn)
        layout.addLayout(btn_row)

        self.setLayout(layout)

    # ── Logic ─────────────────────────────────────────────────────────────
    def _mode_changed(self):
        self._next()

    def _next(self):
        self._awaiting_next = False
        self.input_field.clear()
        self.input_field.setEnabled(True)
        self.label_feedback.setText("")
        self.label_feedback.setStyleSheet("")
        self.check_btn.setEnabled(True)
        self.next_btn.setEnabled(False)

        mode = self.mode_combo.currentText()
        if mode == "Letter → NATO word":
            self._current_key = random.choice(list(NATO_PHONETIC_DICT.keys()))
            self.label_prompt.setText(self._current_key)
            self.label_prompt_desc.setText("Type the NATO phonetic word:")
        else:
            self._current_key = random.choice(list(NATO_PHONETIC_DICT.keys()))
            word = NATO_PHONETIC_DICT[self._current_key]
            self.label_prompt.setText(word)
            self.label_prompt_desc.setText("Type the letter for this word:")

        self.input_field.setFocus()

    def _check(self):
        if self._awaiting_next:
            self._next()
            return
        user = self.input_field.text().strip().upper()
        mode = self.mode_combo.currentText()

        if mode == "Letter → NATO word":
            expected = NATO_PHONETIC_DICT[self._current_key].upper()
        else:
            expected = self._current_key.upper()

        self._score_total += 1
        if user == expected:
            self._score_correct += 1
            self.label_feedback.setText(f"Correct!   {expected}")
            self.label_feedback.setStyleSheet("color: #4caf50;")
        else:
            self.label_feedback.setText(f"Wrong!   Answer: {expected}")
            self.label_feedback.setStyleSheet("color: #f44336;")

        pct = round(self._score_correct / self._score_total * 100)
        self.label_score.setText(
            f"Score: {self._score_correct}/{self._score_total}  ({pct}%)"
        )
        self.input_field.setEnabled(False)
        self.check_btn.setEnabled(False)
        self.next_btn.setEnabled(True)
        self._awaiting_next = True

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

    def closeEvent(self, event):
        if self._score_total > 0:
            log_session(
                "Phonetic Drill",
                correct=self._score_correct,
                total=self._score_total
            )
        if self.return_callback:
            self.return_callback()
        event.accept()


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    win = PhoneticDrill()
    win.show()
    sys.exit(app.exec_())
