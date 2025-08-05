# morse_handler.py
import dicts



class MorseHandler:
    def __init__(self):
        self.current_symbol = ""
        self.decoded_text = ""

    def handle_key(self, key_code):
        from PyQt5.QtCore import Qt

        if key_code == Qt.Key_Q:
            self.current_symbol += "."
        elif key_code == Qt.Key_E:
            self.current_symbol += "-"
        elif key_code == Qt.Key_Space:
            self._commit_current_symbol()
        elif key_code == Qt.Key_Backspace:
            self._handle_backspace()
        elif key_code == Qt.Key_Slash or key_code == Qt.Key_Tab:
            self.decoded_text += " "
        else:
            return False
        return True

    def _commit_current_symbol(self):
        if self.current_symbol:
            char = morse_dict.MORSE_CODE_DICT.get(self.current_symbol, '?')
            self.decoded_text += char
            self.current_symbol = ""

    def _handle_backspace(self):
        if self.current_symbol:
            self.current_symbol = self.current_symbol[:-1]
        elif self.decoded_text:
            self.decoded_text = self.decoded_text[:-1]

    def get_morse_buffer(self):
        return self.current_symbol

    def get_decoded_text(self):
        return self.decoded_text

    def clear(self):
        self.current_symbol = ""
        self.decoded_text = ""
