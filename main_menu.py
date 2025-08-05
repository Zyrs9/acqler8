# main_menu.py

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from tra import MyApp  # Translation app
from morse2svg import run_morse2svg_gui # https://github.com/aalex954
from svg2morse import run_svg2morse_gui # https://github.com/aalex954


class MainMenu(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Morse Tools Launcher")
        self.setGeometry(300, 200, 400, 300)
        self.child_window = None

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Choose a Morse Tool:"))

        self.realtime_button = QPushButton("Real-Time Morse App")
        self.realtime_button.clicked.connect(self.launch_realtime)
        layout.addWidget(self.realtime_button)

        self.svg2morse_button = QPushButton("Decode Morse from Image")
        self.svg2morse_button.clicked.connect(run_svg2morse_gui)
        layout.addWidget(self.svg2morse_button)

        self.morse2svg_button = QPushButton("Generate SVG from Morse")
        self.morse2svg_button.clicked.connect(run_morse2svg_gui)
        layout.addWidget(self.morse2svg_button)

        self.setLayout(layout)

    def launch_realtime(self):
        self.child_window = MyApp()
        self.child_window.show()
        self.hide()  # Optional: hide menu while app is open


if __name__ == "__main__":
    app = QApplication(sys.argv)
    menu = MainMenu()
    menu.show()
    sys.exit(app.exec_())
