# session_stats.py
# Session Progress & Stats — persistent JSON log of practice sessions.
# Records WPM, accuracy per tool, and overall progress over time.

import json
import os
import time
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame, QTabWidget
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STATS_FILE   = os.path.join(_SCRIPT_DIR, "session_stats.json")


# ── Public API (called by other modules) ──────────────────────────────────────
def log_session(tool: str, correct: int, total: int, wpm: float = 0.0):
    """
    Append one session record to the stats file.

    tool    : e.g. "Morse Exercise", "WPM Trainer", "Send Practice"
    correct : number of correct answers
    total   : total attempts
    wpm     : average WPM if applicable (0 = N/A)
    """
    record = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "tool": tool,
        "correct": correct,
        "total": total,
        "accuracy": round(correct / total * 100, 1) if total else 0.0,
        "wpm": round(wpm, 1),
    }
    records = _load()
    records.append(record)
    _save(records)


def _load() -> list:
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return []


def _save(records: list):
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)


# ── Stats Viewer Widget ────────────────────────────────────────────────────────
class StatsViewer(QWidget):
    def __init__(self, return_callback=None):
        super().__init__()
        self.return_callback = return_callback
        self.setWindowTitle("Session Stats")
        self.setGeometry(200, 100, 700, 500)
        self._build_ui()
        self._load_data()

    def _build_ui(self):
        layout = QVBoxLayout()

        header_row = QHBoxLayout()
        title = QLabel("Session Progress & Stats")
        title.setFont(QFont("Arial", 13, QFont.Bold))
        header_row.addWidget(title)
        header_row.addStretch()

        self.clear_btn = QPushButton("Clear All")
        self.clear_btn.clicked.connect(self._clear)
        header_row.addWidget(self.clear_btn)

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self._load_data)
        header_row.addWidget(self.refresh_btn)

        layout.addLayout(header_row)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: #444;")
        layout.addWidget(line)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._make_log_tab(),      "Session Log")
        self.tabs.addTab(self._make_summary_tab(),  "Summary by Tool")
        layout.addWidget(self.tabs)

        self.setLayout(layout)

    # ── Log tab ───────────────────────────────────────────────────────────────
    def _make_log_tab(self) -> QWidget:
        w = QWidget()
        v = QVBoxLayout(w)
        self.log_table = QTableWidget(0, 5)
        self.log_table.setHorizontalHeaderLabels(
            ["Date / Time", "Tool", "Correct", "Total", "Accuracy %"]
        )
        hdr = self.log_table.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(1, QHeaderView.Stretch)
        hdr.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.log_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.log_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.log_table.verticalHeader().setVisible(False)
        v.addWidget(self.log_table)
        return w

    # ── Summary tab ───────────────────────────────────────────────────────────
    def _make_summary_tab(self) -> QWidget:
        w = QWidget()
        v = QVBoxLayout(w)
        self.summary_table = QTableWidget(0, 5)
        self.summary_table.setHorizontalHeaderLabels(
            ["Tool", "Sessions", "Total Attempts", "Avg Accuracy %", "Avg WPM"]
        )
        hdr = self.summary_table.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.Stretch)
        for i in range(1, 5):
            hdr.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        self.summary_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.summary_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.summary_table.verticalHeader().setVisible(False)

        self.label_totals = QLabel("")
        self.label_totals.setFont(QFont("Arial", 10))
        self.label_totals.setStyleSheet("color: #aaa; margin-top: 6px;")

        v.addWidget(self.summary_table)
        v.addWidget(self.label_totals)
        return w

    # ── Data ──────────────────────────────────────────────────────────────────
    def _load_data(self):
        records = _load()

        # Log tab (most recent first)
        self.log_table.setRowCount(0)
        for rec in reversed(records):
            r = self.log_table.rowCount()
            self.log_table.insertRow(r)
            self.log_table.setItem(r, 0, QTableWidgetItem(rec.get("timestamp", "")))
            self.log_table.setItem(r, 1, QTableWidgetItem(rec.get("tool", "")))
            self.log_table.setItem(r, 2, QTableWidgetItem(str(rec.get("correct", 0))))
            self.log_table.setItem(r, 3, QTableWidgetItem(str(rec.get("total", 0))))
            acc = rec.get("accuracy", 0)
            self.log_table.setItem(r, 4, QTableWidgetItem(f"{acc:.1f}"))

        # Summary tab
        by_tool: dict[str, list] = {}
        for rec in records:
            tool = rec.get("tool", "Unknown")
            by_tool.setdefault(tool, []).append(rec)

        self.summary_table.setRowCount(0)
        total_sessions = len(records)
        total_attempts = sum(r.get("total", 0) for r in records)

        for tool, recs in sorted(by_tool.items()):
            sessions   = len(recs)
            attempts   = sum(r.get("total", 0) for r in recs)
            avg_acc    = sum(r.get("accuracy", 0) for r in recs) / sessions
            wpm_vals   = [r.get("wpm", 0) for r in recs if r.get("wpm", 0) > 0]
            avg_wpm    = sum(wpm_vals) / len(wpm_vals) if wpm_vals else 0

            r = self.summary_table.rowCount()
            self.summary_table.insertRow(r)
            self.summary_table.setItem(r, 0, QTableWidgetItem(tool))
            self.summary_table.setItem(r, 1, QTableWidgetItem(str(sessions)))
            self.summary_table.setItem(r, 2, QTableWidgetItem(str(attempts)))
            self.summary_table.setItem(r, 3, QTableWidgetItem(f"{avg_acc:.1f}"))
            self.summary_table.setItem(r, 4, QTableWidgetItem(f"{avg_wpm:.1f}" if avg_wpm else "—"))

        self.label_totals.setText(
            f"Total sessions: {total_sessions}   |   Total attempts: {total_attempts}"
        )

    def _clear(self):
        _save([])
        self._load_data()

    def closeEvent(self, event):
        if self.return_callback:
            self.return_callback()
        event.accept()


if __name__ == "__main__":
    import sys
    # Demo: log a fake session so the viewer has data to show
    log_session("Demo Tool", correct=8, total=10, wpm=12.5)
    app = QApplication(sys.argv)
    win = StatsViewer()
    win.show()
    sys.exit(app.exec_())
