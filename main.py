import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QPushButton, QTextEdit
)
from PyQt5.QtCore import Qt, QObject, QEvent
from morse_handler import MorseHandler


class KeyEventFilter(QObject):
    def __init__(self, handler, update_callback):
        super().__init__()
        self.morse_handler = handler
        self.update_callback = update_callback

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress:
            if self.morse_handler.handle_key(event.key()):
                self.update_callback()
                return True
        return False


class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Real-Time Morse Decoder")
        self.setGeometry(100, 100, 600, 500)

        self.morse = MorseHandler()

        self.init_ui()

        # Install event filter to capture global key events
        self.key_filter = KeyEventFilter(self.morse, self.update_display)
        QApplication.instance().installEventFilter(self.key_filter)

    def init_ui(self):
        layout = QVBoxLayout()

        self.label = QLabel("Type Morse: Q (.)  E (-)  Space = next letter  Tab = next word")
        layout.addWidget(self.label)

        self.morse_display = QTextEdit()
        self.morse_display.setReadOnly(True)
        layout.addWidget(QLabel("Current Morse Symbol:"))
        layout.addWidget(self.morse_display)

        self.decoded_display = QTextEdit()
        self.decoded_display.setReadOnly(True)
        layout.addWidget(QLabel("Decoded Text (live):"))
        layout.addWidget(self.decoded_display)

        self.clear_button = QPushButton("Clear All")
        self.clear_button.clicked.connect(self.clear_all)
        layout.addWidget(self.clear_button)

        self.setLayout(layout)

    def update_display(self):
        self.morse_display.setPlainText(self.morse.get_morse_buffer())
        self.decoded_display.setPlainText(self.morse.get_decoded_text())

    def clear_all(self):
        self.morse.clear()
        self.update_display()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
