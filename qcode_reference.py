# qcode_reference.py
# Q-Code and CW Abbreviations reference viewer with live search.

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QTableWidget, QTableWidgetItem, QTabWidget, QHeaderView, QFrame
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from dicts import Q_CODES, CW_ABBREVIATIONS


class ReferenceWindow(QWidget):
    def __init__(self, return_callback=None):
        super().__init__()
        self.return_callback = return_callback
        self.setWindowTitle("Q-Code & CW Abbreviations Reference")
        self.setGeometry(200, 100, 660, 540)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()

        title = QLabel("Q-Code & CW Abbreviations Reference")
        title.setFont(QFont("Arial", 13, QFont.Bold))
        layout.addWidget(title)

        # Search bar
        search_row = QHBoxLayout()
        search_row.addWidget(QLabel("Search:"))
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Type to filter…")
        self.search_box.textChanged.connect(self._filter)
        search_row.addWidget(self.search_box)
        layout.addLayout(search_row)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.addTab(self._make_qcode_tab(),  "Q-Codes")
        self.tabs.addTab(self._make_abbr_tab(),   "CW Abbreviations")
        self.tabs.currentChanged.connect(lambda _: self._filter(self.search_box.text()))
        layout.addWidget(self.tabs)

        self.setLayout(layout)

    # ── Q-Code tab ────────────────────────────────────────────────────────
    def _make_qcode_tab(self) -> QWidget:
        w = QWidget()
        v = QVBoxLayout(w)
        self.qcode_table = QTableWidget(0, 3)
        self.qcode_table.setHorizontalHeaderLabels(["Code", "Meaning", "Usage / Example"])
        self.qcode_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.qcode_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.qcode_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.qcode_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.qcode_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.qcode_table.verticalHeader().setVisible(False)
        self._qcode_rows = list(Q_CODES.items())          # (code, (meaning, example))
        self._fill_qcode(self._qcode_rows)
        v.addWidget(self.qcode_table)
        return w

    def _fill_qcode(self, rows):
        self.qcode_table.setRowCount(0)
        for code, (meaning, example) in rows:
            r = self.qcode_table.rowCount()
            self.qcode_table.insertRow(r)
            self.qcode_table.setItem(r, 0, QTableWidgetItem(code))
            self.qcode_table.setItem(r, 1, QTableWidgetItem(meaning))
            self.qcode_table.setItem(r, 2, QTableWidgetItem(example))

    # ── Abbreviation tab ──────────────────────────────────────────────────
    def _make_abbr_tab(self) -> QWidget:
        w = QWidget()
        v = QVBoxLayout(w)
        self.abbr_table = QTableWidget(0, 2)
        self.abbr_table.setHorizontalHeaderLabels(["Abbreviation", "Meaning"])
        self.abbr_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.abbr_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.abbr_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.abbr_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.abbr_table.verticalHeader().setVisible(False)
        self._abbr_rows = list(CW_ABBREVIATIONS.items())  # (abbr, meaning)
        self._fill_abbr(self._abbr_rows)
        v.addWidget(self.abbr_table)
        return w

    def _fill_abbr(self, rows):
        self.abbr_table.setRowCount(0)
        for abbr, meaning in rows:
            r = self.abbr_table.rowCount()
            self.abbr_table.insertRow(r)
            self.abbr_table.setItem(r, 0, QTableWidgetItem(abbr))
            self.abbr_table.setItem(r, 1, QTableWidgetItem(meaning))

    # ── Filter ────────────────────────────────────────────────────────────
    def _filter(self, text: str):
        q = text.upper()
        if self.tabs.currentIndex() == 0:
            filtered = [(c, m) for c, m in self._qcode_rows
                        if q in c or q in m[0].upper() or q in m[1].upper()]
            self._fill_qcode(filtered)
        else:
            filtered = [(a, m) for a, m in self._abbr_rows
                        if q in a or q in m.upper()]
            self._fill_abbr(filtered)

    def closeEvent(self, event):
        if self.return_callback:
            self.return_callback()
        event.accept()


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    win = ReferenceWindow()
    win.show()
    sys.exit(app.exec_())
