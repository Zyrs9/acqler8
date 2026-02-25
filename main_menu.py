import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QLabel, QFrame, QGraphicsDropShadowEffect
)
from PyQt5.QtGui import QFont, QColor, QPalette
from PyQt5.QtCore import Qt
from tools.morse2svg import run_morse2svg_gui
from tools.svg2morse import Svg2MorseWindow
from training.morse_exercise import MorseExerciseApp
from tools.text2morse_window import TextToMorseWindow
from training.wpm_trainer import WpmTrainer
from training.send_practice import SendPractice
from tools.qcode_reference import ReferenceWindow
from training.phonetic_drill import PhoneticDrill
from session_stats import StatsViewer
from tools.tra import MyApp


# ── Dark theme stylesheet ─────────────────────────────────────────────────────
_DARK_STYLE = """
QWidget {
    background-color: #1a1a2e;
    color: #e0e0e0;
    font-family: 'Segoe UI', Arial, sans-serif;
}
QLabel {
    color: #c0c0d0;
}
QFrame[frameShape="4"] {          /* HLine */
    background-color: #2a2a4a;
    max-height: 1px;
    border: none;
}
QPushButton {
    background-color: #16213e;
    color: #d0d8ff;
    border: 1px solid #2a3a6a;
    border-radius: 7px;
    padding: 7px 14px;
    font-size: 11pt;
    text-align: left;
}
QPushButton:hover {
    background-color: #0f3460;
    border-color: #5577cc;
    color: #ffffff;
}
QPushButton:pressed {
    background-color: #0a2240;
    border-color: #7799ee;
}
QTextEdit, QLineEdit {
    background-color: #12122a;
    color: #d8deff;
    border: 1px solid #2a3a6a;
    border-radius: 5px;
    padding: 4px;
    selection-background-color: #3355aa;
}
QComboBox, QSpinBox {
    background-color: #12122a;
    color: #d8deff;
    border: 1px solid #2a3a6a;
    border-radius: 5px;
    padding: 3px 8px;
}
QComboBox::drop-down { border: none; }
QComboBox QAbstractItemView {
    background-color: #1a1a3a;
    selection-background-color: #3355aa;
}
QCheckBox { color: #d0d0e8; }
QCheckBox::indicator {
    width: 14px; height: 14px;
    border: 1px solid #4455aa;
    border-radius: 3px;
    background: #12122a;
}
QCheckBox::indicator:checked { background: #3355cc; }
QSlider::groove:horizontal {
    background: #2a2a4a; height: 4px; border-radius: 2px;
}
QSlider::handle:horizontal {
    background: #5577cc; width: 14px; height: 14px;
    margin: -5px 0; border-radius: 7px;
}
QSlider::sub-page:horizontal { background: #3355aa; border-radius: 2px; }
QScrollBar:vertical {
    background: #12122a; width: 8px;
}
QScrollBar::handle:vertical {
    background: #3344aa; border-radius: 4px;
}
QTabWidget::pane { border: 1px solid #2a3a6a; }
QTabBar::tab {
    background: #16213e; color: #aaaacc;
    padding: 6px 16px; border-radius: 4px 4px 0 0;
}
QTabBar::tab:selected { background: #0f3460; color: #ffffff; }
QHeaderView::section {
    background-color: #16213e; color: #aaaacc;
    font-weight: bold; padding: 4px;
    border: 1px solid #2a3a6a;
}
QTableWidget { gridline-color: #2a2a4a; }
QToolTip {
    background-color: #0f3460;
    color: #e0e8ff;
    border: 1px solid #5577cc;
    padding: 4px 8px;
    border-radius: 4px;
}
"""

_SECTION_COLORS = {
    "TRAINING":     "#4fc3f7",
    "INPUT":        "#a5d6a7",
    "RADIO":        "#ffcc80",
    "IMAGE":        "#ce93d8",
    "PROGRESS":     "#f48fb1",
}


def _section_label(text: str, color: str = "#7888bb") -> QLabel:
    lbl = QLabel(f"  {text}")
    lbl.setFont(QFont("Segoe UI", 8, QFont.Bold))
    lbl.setStyleSheet(f"color: {color}; letter-spacing: 2px; margin-top: 4px;")
    return lbl


def _divider() -> QFrame:
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    line.setFixedHeight(1)
    line.setStyleSheet("background-color: #252545; border: none;")
    return line


class MainMenu(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Morse / CW Toolkit")
        self.setGeometry(300, 100, 440, 700)
        self.child_window = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(3)
        layout.setContentsMargins(14, 14, 14, 14)

        # ── Title ──────────────────────────────────────────────────────────
        title = QLabel("Morse / CW Toolkit")
        title.setFont(QFont("Segoe UI", 17, QFont.Bold))
        title.setStyleSheet("color: #a0b8ff; margin-bottom: 4px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Amateur Radio Practice & Conversion Suite")
        subtitle.setFont(QFont("Segoe UI", 9))
        subtitle.setStyleSheet("color: #555577; margin-bottom: 6px;")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)

        layout.addWidget(_divider())

        # ── Training ───────────────────────────────────────────────────────
        layout.addWidget(_section_label("▸  TRAINING", _SECTION_COLORS["TRAINING"]))
        self._btn(layout, "Morse Exercise",
                  "Learn the alphabet: hear → identify each letter",
                  self.launch_exercise)
        self._btn(layout, "WPM Speed Trainer",
                  "Decode random Morse sequences to improve speed",
                  self.launch_wpm_trainer)
        self._btn(layout, "Send Practice  (WPM)",
                  "Encode words with Q/E — get timed WPM score",
                  self.launch_send_practice)
        self._btn(layout, "Phonetic Alphabet Drill",
                  "Practise NATO phonetics in both directions",
                  self.launch_phonetic_drill)

        layout.addWidget(_divider())

        # ── Input & Conversion ─────────────────────────────────────────────
        layout.addWidget(_section_label("▸  INPUT & CONVERSION", _SECTION_COLORS["INPUT"]))
        self._btn(layout, "Real-Time Morse Input",
                  "Type Q/E live and see decoded text in real time",
                  self.launch_realtime)
        self._btn(layout, "Text → Morse Converter",
                  "Convert any text (incl. Turkish) to Morse and play it",
                  self.launch_text2morse)

        layout.addWidget(_divider())

        # ── Radio Utilities ────────────────────────────────────────────────
        layout.addWidget(_section_label("▸  RADIO UTILITIES", _SECTION_COLORS["RADIO"]))
        self._btn(layout, "Q-Code & CW Abbreviations",
                  "Searchable reference of Q-codes, prosigns, and abbreviations",
                  self.launch_reference)

        layout.addWidget(_divider())

        # ── Image Tools ────────────────────────────────────────────────────
        layout.addWidget(_section_label("▸  IMAGE TOOLS", _SECTION_COLORS["IMAGE"]))
        self._btn(layout, "Decode Morse from Image",
                  "Read green-bar Morse signal from a PNG/JPG image",
                  self.launch_svg2morse)
        self._btn(layout, "Generate SVG from Morse",
                  "Create a visual Morse waveform SVG file",
                  run_morse2svg_gui)

        layout.addWidget(_divider())

        # ── Progress ───────────────────────────────────────────────────────
        layout.addWidget(_section_label("▸  PROGRESS", _SECTION_COLORS["PROGRESS"]))
        self._btn(layout, "Session Stats",
                  "View accuracy and WPM history across all training tools",
                  self.launch_stats)

        layout.addStretch()
        self.setLayout(layout)

    def _btn(self, layout, label: str, tooltip: str, slot) -> QPushButton:
        btn = QPushButton(f"  {label}")
        btn.setFont(QFont("Segoe UI", 11))
        btn.setMinimumHeight(36)
        btn.setToolTip(tooltip)
        btn.clicked.connect(slot)
        layout.addWidget(btn)
        return btn

    # ── Launchers ──────────────────────────────────────────────────────────
    def launch_exercise(self):
        self.child_window = MorseExerciseApp(return_callback=self.show_main)
        self._show_child()

    def launch_wpm_trainer(self):
        self.child_window = WpmTrainer(return_callback=self.show_main)
        self._show_child()

    def launch_send_practice(self):
        self.child_window = SendPractice(return_callback=self.show_main)
        self._show_child()

    def launch_phonetic_drill(self):
        self.child_window = PhoneticDrill(return_callback=self.show_main)
        self._show_child()

    def launch_realtime(self):
        self.child_window = MyApp(return_callback=self.show_main)
        self._show_child()

    def launch_text2morse(self):
        self.child_window = TextToMorseWindow(return_callback=self.show_main)
        self._show_child()

    def launch_svg2morse(self):
        self.child_window = Svg2MorseWindow(return_callback=self.show_main)
        self._show_child()

    def launch_reference(self):
        self.child_window = ReferenceWindow(return_callback=self.show_main)
        self._show_child()

    def launch_stats(self):
        self.child_window = StatsViewer(return_callback=self.show_main)
        self._show_child()

    def _show_child(self):
        if self.child_window:
            self.child_window.show()
            self.hide()

    def show_main(self):
        self.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(_DARK_STYLE)
    menu = MainMenu()
    menu.show()
    sys.exit(app.exec_())
