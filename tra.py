import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QPushButton, QTextEdit
)
from PyQt5.QtCore import Qt, QObject, QEvent
from morse_handler import MorseHandler
from text2morse_window import TextToMorseWindow
import cw_audio


class KeyEventFilter(QObject):
    def __init__(self, handler, update_callback):
        super().__init__()
        self.morse_handler = handler
        self.update_callback = update_callback

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress:
            key = event.key()

            if key == Qt.Key_Return or key == Qt.Key_Enter:
                self.morse_handler.clear()
                self.update_callback()
                return True

            # Play sidetone feedback
            if key == Qt.Key_Q:
                cw_audio.play_dit()
            elif key == Qt.Key_E:
                cw_audio.play_dah()

            if self.morse_handler.handle_key(key):
                self.update_callback()
                return True
        return False


class MyApp(QWidget):
    def __init__(self, return_callback=None):
        super().__init__()
        self.setWindowTitle("Morse Input (Real-Time)")
        self.setGeometry(100, 100, 600, 500)

        self.morse = MorseHandler()
        self.text_to_morse_window = None
        self.return_callback = return_callback

        self.init_ui()

        # Global key listener
        self.key_filter = KeyEventFilter(self.morse, self.update_display)
        QApplication.instance().installEventFilter(self.key_filter)

    def init_ui(self):
        layout = QVBoxLayout()

        self.label = QLabel("Q=dot, E=dash, SPACE=letter, TAB=word, ENTER=clear")
        layout.addWidget(self.label)

        self.morse_display = QTextEdit()
        self.morse_display.setReadOnly(True)
        layout.addWidget(QLabel("Current Morse Symbol:"))
        layout.addWidget(self.morse_display)

        self.decoded_display = QTextEdit()
        self.decoded_display.setReadOnly(True)
        layout.addWidget(QLabel("Decoded Text (live):"))
        layout.addWidget(self.decoded_display)

        self.clear_button = QPushButton("Clear All (Enter)")
        self.clear_button.clicked.connect(self.clear_all)
        layout.addWidget(self.clear_button)

        self.switch_button = QPushButton("Switch to Text → Morse Mode")
        self.switch_button.clicked.connect(self.open_text_to_morse)
        layout.addWidget(self.switch_button)

        self.setLayout(layout)

    def update_display(self):
        self.morse_display.setPlainText(self.morse.get_morse_buffer())
        self.decoded_display.setPlainText(self.morse.get_decoded_text())

    def clear_all(self):
        self.morse.clear()
        self.update_display()

    def open_text_to_morse(self):
        QApplication.instance().removeEventFilter(self.key_filter)

        if self.text_to_morse_window is None or not self.text_to_morse_window.isVisible():
            self.text_to_morse_window = TextToMorseWindow(self.return_from_text_to_morse)
            self.text_to_morse_window.show()
        self.hide()

    def return_from_text_to_morse(self):
        # Re-enable the key filter when returning
        QApplication.instance().installEventFilter(self.key_filter)

        if self.text_to_morse_window is not None:
            self.text_to_morse_window.hide()

        self.show()  # bring main window back

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)

    def closeEvent(self, event):
        QApplication.instance().removeEventFilter(self.key_filter)
        if self.return_callback:
            self.return_callback()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
