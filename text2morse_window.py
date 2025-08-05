# text_to_morse_window.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QTextEdit, QLineEdit
)
from morse_dict import MORSE_CODE_DICT, normalize_turkish_characters



class TextToMorseWindow(QWidget):
    def __init__(self, return_callback):
        super().__init__()
        self.setWindowTitle("Text to Morse Converter")
        self.setGeometry(200, 200, 600, 400)

        self.return_callback = return_callback  # function to go back to main

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Enter Text:"))
        self.input_field = QLineEdit()
        self.input_field.textChanged.connect(self.convert_to_morse)
        layout.addWidget(self.input_field)

        layout.addWidget(QLabel("Morse Output:"))
        self.output_field = QTextEdit()
        self.output_field.setReadOnly(True)
        layout.addWidget(self.output_field)

        self.back_button = QPushButton("Back to Morse Input Mode")
        self.back_button.clicked.connect(self.go_back)
        layout.addWidget(self.back_button)

        self.setLayout(layout)

    def convert_to_morse(self):
        raw_text = self.input_field.text()
        normalized = normalize_turkish_characters(raw_text.upper())
#       print(f"Normalized: {normalized}") debug purpose
        morse = []

        for char in normalized:
            code = MORSE_CODE_DICT.get(char, '?')
            morse.append(code)

        self.output_field.setPlainText(" ".join(morse))

    def go_back(self):
        if self.return_callback:
            self.return_callback()  # call main window return
        self.hide()
