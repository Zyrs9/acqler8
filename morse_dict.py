# morse_dict.py

MORSE_CODE_DICT = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..',
    'E': '.',  'F': '..-.', 'G': '--.',  'H': '....',
    'I': '..', 'J': '.---', 'K': '-.-',  'L': '.-..',
    'M': '--', 'N': '-.',   'O': '---',  'P': '.--.',
    'Q': '--.-','R': '.-.', 'S': '...',  'T': '-',
    'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
    'Y': '-.--','Z': '--..',
    '0': '-----', '1': '.----', '2': '..---', '3': '...--',
    '4': '....-', '5': '.....', '6': '-....', '7': '--...',
    '8': '---..', '9': '----.',
    ' ': '/'
}
TURKISH_REPLACEMENTS = {
    'ç': 'ch',
    'Ç': 'CH',
    'ş': 'sh',
    'Ş': 'SH',
    'ğ': 'g',
    'Ğ': 'G',
    'ü': 'u',
    'Ü': 'U',
    'ö': 'o',
    'Ö': 'O',
    'ı': 'i',
    'İ': 'I'
}

def normalize_turkish_characters(text):
    result = []
    for char in text:
        if char in TURKISH_REPLACEMENTS:
            result.append(TURKISH_REPLACEMENTS[char])
        else:
            result.append(char)
    return ''.join(result)
