# dicts.py
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
NATO_PHONETIC_DICT = {
    "A": "Alpha",
    "B": "Bravo",
    "C": "Charlie",
    "D": "Delta",
    "E": "Echo",
    "F": "Foxtrot",
    "G": "Golf",
    "H": "Hotel",
    "I": "India",
    "J": "Juliett",
    "K": "Kilo",
    "L": "Lima",
    "M": "Mike",
    "N": "November",
    "O": "Oscar",
    "P": "Papa",
    "Q": "Quebec",
    "R": "Romeo",
    "S": "Sierra",
    "T": "Tango",
    "U": "Uniform",
    "V": "Victor",
    "W": "Whiskey",
    "X": "X-ray",
    "Y": "Yankee",
    "Z": "Zulu"
}


def normalize_turkish_characters(text):
    result = []
    for char in text:
        if char in TURKISH_REPLACEMENTS:
            result.append(TURKISH_REPLACEMENTS[char])
        else:
            result.append(char)
    return ''.join(result)


# ── Q-Codes ────────────────────────────────────────────────────────────────────
# Each entry: (short_meaning, example_usage)
Q_CODES = {
    "QRA": ("Station name",         "What is the name of your station?"),
    "QRB": ("Distance",             "How far are you from my station?"),
    "QRG": ("Exact frequency",      "What is my exact frequency?"),
    "QRH": ("Frequency varies",     "Does my frequency vary?"),
    "QRI": ("Tone quality",         "How is the tone of my transmission?"),
    "QRK": ("Signal readability",   "What is the readability of my signals? (1–5)"),
    "QRL": ("Are you busy?",        "Are you busy? / I am busy."),
    "QRM": ("Man-made interference","Are you being interfered with?"),
    "QRN": ("Static / noise",       "Are you troubled by static?"),
    "QRO": ("Increase power",       "Shall I increase transmitter power?"),
    "QRP": ("Decrease power",       "Shall I decrease transmitter power?  (low-power ops)"),
    "QRQ": ("Send faster",          "Shall I send faster?"),
    "QRR": ("Ready for automatic",  "Are you ready for automatic operation?"),
    "QRS": ("Send slower",          "Shall I send more slowly?"),
    "QRT": ("Stop sending",         "Shall I cease transmission?"),
    "QRU": ("Nothing for you",      "Have you anything for me? / Nothing for you."),
    "QRV": ("Ready",                "Are you ready? / I am ready."),
    "QRX": ("Wait / stand by",      "When will you call me again?"),
    "QRZ": ("Who is calling?",      "Who is calling me?"),
    "QSA": ("Signal strength",      "What is the strength of my signals? (1–5)"),
    "QSB": ("Signal fading",        "Are my signals fading?"),
    "QSD": ("Defective keying",     "Is my keying defective?"),
    "QSK": ("Break-in",             "Can you hear me between your signals?"),
    "QSL": ("Acknowledge receipt",  "Can you acknowledge receipt?"),
    "QSM": ("Repeat last message",  "Shall I repeat the last message?"),
    "QSO": ("Contact / QSO",        "Can you communicate with … directly?"),
    "QSP": ("Relay to",             "Will you relay to …?"),
    "QST": ("General call",         "General call preceding message to all amateurs."),
    "QSX": ("Listen on…",           "Will you listen to … on … kHz?"),
    "QSY": ("Change frequency",     "Shall I change to transmit on another frequency?"),
    "QTH": ("Location",             "What is your location?"),
    "QTR": ("Time",                 "What is the correct time?"),
}

# ── CW Abbreviations ──────────────────────────────────────────────────────────
CW_ABBREVIATIONS = {
    "73":  "Best regards",
    "88":  "Love and kisses",
    "AR":  "End of message",
    "AS":  "Wait / stand by",
    "BK":  "Break / invite any station to transmit",
    "BT":  "Break (separator) — equivalent to paragraph",
    "CQ":  "General call to any station",
    "CW":  "Continuous wave (Morse code mode)",
    "DE":  "From (used between callsigns)",
    "DR":  "Dear",
    "DX":  "Long distance / rare station",
    "ES":  "And",
    "FB":  "Fine business — excellent!",
    "GA":  "Good afternoon / go ahead",
    "GE":  "Good evening",
    "GM":  "Good morning",
    "GN":  "Good night",
    "GUD": "Good",
    "HI":  "Laughter (CW version of 'haha')",
    "HR":  "Here / hear",
    "HW":  "How? / How copy?",
    "K":   "Invitation to transmit (any station)",
    "KN":  "Invitation to transmit (specific station only)",
    "NR":  "Number",
    "OM":  "Old man (friendly term for any operator)",
    "OPR": "Operator",
    "PSE": "Please",
    "R":   "Roger — received / understood",
    "RIG": "Radio equipment",
    "RPT": "Repeat",
    "RST": "Readability, Signal, Tone (signal report)",
    "SK":  "End of contact (sign off)",
    "SRI": "Sorry",
    "TMW": "Tomorrow",
    "TNX": "Thanks",
    "TU":  "Thank you",
    "UR":  "Your / you are",
    "VE":  "Understood (European)",
    "VY":  "Very",
    "WPM": "Words per minute",
    "XYL": "Wife (ex-young lady)",
    "YL":  "Young lady (any female operator)",
}
