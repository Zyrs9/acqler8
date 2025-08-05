import random
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout
)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt

from dicts import MORSE_CODE_DICT


class MorseExerciseApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Morse Exercise")
        self.setGeometry(200, 200, 400, 300)

        # Only include A-Z (no digits or symbols)
        self.letters = [k for k in MORSE_CODE_DICT.keys() if k.isalpha()]
        self.mnemonic_path = "mnemonic_letter_images"
        self.current_letter = ""
        self.user_input = ""
        self.awaiting_next = False

        self.label_letter = QLabel("", self)
        self.label_letter.setFont(QFont("Arial", 48))
        self.label_letter.setAlignment(Qt.AlignCenter)

        self.label_feedback = QLabel("", self)
        self.label_feedback.setFont(QFont("Arial", 14))
        self.label_feedback.setAlignment(Qt.AlignCenter)

        self.label_image = QLabel("", self)
        self.label_image.setAlignment(Qt.AlignCenter)
        self.label_image.hide()

        self.reset_button = QPushButton("Next", self)
        self.reset_button.clicked.connect(self.next_letter)

        layout = QVBoxLayout()
        layout.addWidget(self.label_letter)
        layout.addWidget(self.label_feedback)
        layout.addWidget(self.label_image)
        layout.addWidget(self.reset_button)

        self.setLayout(layout)
        self.next_letter()

    def next_letter(self):
        self.current_letter = random.choice(self.letters)
        self.user_input = ""
        self.awaiting_next = False
        self.label_letter.setText(self.current_letter)
        self.label_feedback.setText("")
        self.label_image.hide()

    def keyPressEvent(self, event):
        if self.awaiting_next:
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                self.next_letter()
            return

        if event.key() == Qt.Key_Q:
            self.user_input += "."
        elif event.key() == Qt.Key_E:
            self.user_input += "-"
        elif event.key() == Qt.Key_Backspace:
            self.user_input = self.user_input[:-1]
        elif event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.check_input()

        self.label_feedback.setText(self.user_input)

    def check_input(self):
        expected = MORSE_CODE_DICT.get(self.current_letter, "")
        if self.user_input == expected:
            self.label_feedback.setText("Correct!")
            self.next_letter()
        else:
            self.label_feedback.setText(f"Wrong! Expected: {expected}")
            self.show_mnemonic_image()
            self.awaiting_next = True

    def show_mnemonic_image(self):
        files = os.listdir(self.mnemonic_path)
        match = next((f for f in files if f.startswith(self.current_letter + "_")), None)
        if match:
            path = os.path.join(self.mnemonic_path, match)
            pixmap = QPixmap(path).scaledToWidth(200, Qt.SmoothTransformation)
            self.label_image.setPixmap(pixmap)
            self.label_image.show()


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    win = MorseExerciseApp()
    win.show()
    sys.exit(app.exec_())
