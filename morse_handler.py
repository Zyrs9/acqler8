# morse_handler.py

MORSE_CODE_DICT = {
    '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D',
    '.': 'E', '..-.': 'F', '--.': 'G', '....': 'H',
    '..': 'I', '.---': 'J', '-.-': 'K', '.-..': 'L',
    '--': 'M', '-.': 'N', '---': 'O', '.--.': 'P',
    '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T',
    '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X',
    '-.--': 'Y', '--..': 'Z', '-----': '0', '.----': '1',
    '..---': '2', '...--': '3', '....-': '4', '.....': '5',
    '-....': '6', '--...': '7', '---..': '8', '----.': '9'
}


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
            char = MORSE_CODE_DICT.get(self.current_symbol, '?')
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
