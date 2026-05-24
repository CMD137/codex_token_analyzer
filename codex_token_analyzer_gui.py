from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSpinBox,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QHeaderView,
)

from analyzer_core import load_report

THREAD_COLUMNS = [
    ("Title", "title"),
    ("Last Activity", "last_activity"),
    ("Input", "input_tokens"),
    ("Cached", "cached_input_tokens"),
    ("Output", "output_tokens"),
    ("Reasoning", "reasoning_output_tokens"),
    ("Total", "total_tokens"),
    ("Cache Hit %", "cache_hit_rate"),
]


class AnalyzerWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.current_report: dict | None = None
        self.current_threads: list[dict] = []

        self.setWindowTitle("Codex Token Analyzer")
        self.resize(1400, 820)

        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)

        controls_layout = QHBoxLayout()
        controls_layout.addWidget(QLabel("Window Days"))

        self.days_spin = QSpinBox()
        self.days_spin.setRange(1, 365)
        self.days_spin.setValue(7)
        self.days_spin.setToolTip("Choose how many recent days to include in the report.")
        controls_layout.addWidget(self.days_spin)

        self.refresh_button = QPushButton("Refresh")
        controls_layout.addWidget(self.refresh_button)
        controls_layout.addStretch()
        root_layout.addLayout(controls_layout)

        root_layout.addWidget(self._build_summary_group())
        root_layout.addWidget(self._build_rate_limits_group())
        root_layout.addWidget(self._build_main_splitter(), stretch=1)

        self.refresh_button.clicked.connect(self.refresh_report)
        self.days_spin.valueChanged.connect(self.refresh_report)
        self.thread_table.itemSelectionChanged.connect(self.update_details)

        self.statusBar().showMessage("Ready")
        self.refresh_report()

    def _build_summary_group(self) -> QGroupBox:
        group = QGroupBox("Summary")
        layout = QGridLayout(group)

        self.summary_labels = {
            "window_start": QLabel("-"),
            "window_end": QLabel("-"),
            "active_thread_count": QLabel("-"),
            "input_tokens": QLabel("-"),
            "cached_input_tokens": QLabel("-"),
            "output_tokens": QLabel("-"),
            "reasoning_output_tokens": QLabel("-"),
            "total_tokens": QLabel("-"),
            "aggregate_cache_hit_rate": QLabel("-"),
        }

        rows = [
            ("Window Start", "window_start"),
            ("Window End", "window_end"),
            ("Active Threads", "active_thread_count"),
            ("Input Tokens", "input_tokens"),
            ("Cached Input", "cached_input_tokens"),
            ("Output Tokens", "output_tokens"),
            ("Reasoning Output", "reasoning_output_tokens"),
            ("Total Tokens", "total_tokens"),
            ("Aggregate Cache Hit", "aggregate_cache_hit_rate"),
        ]

        for index, (label_text, key) in enumerate(rows):
            row = index // 3
            col = (index % 3) * 2
            layout.addWidget(QLabel(label_text), row, col)
            layout.addWidget(self.summary_labels[key], row, col + 1)

        return group

    def _build_rate_limits_group(self) -> QGroupBox:
        group = QGroupBox("Rate Limits")
        layout = QFormLayout(group)

        self.rate_limit_labels = {
            "timestamp": QLabel("-"),
            "plan_type": QLabel("-"),
            "primary_used_percent": QLabel("-"),
            "primary_remaining_percent": QLabel("-"),
            "secondary_used_percent": QLabel("-"),
            "secondary_remaining_percent": QLabel("-"),
            "file": QLabel("-"),
        }

        layout.addRow("Timestamp", self.rate_limit_labels["timestamp"])
        layout.addRow("Plan", self.rate_limit_labels["plan_type"])
        layout.addRow("5h Used", self.rate_limit_labels["primary_used_percent"])
        layout.addRow("5h Remaining", self.rate_limit_labels["primary_remaining_percent"])
        layout.addRow("Weekly Used", self.rate_limit_labels["secondary_used_percent"])
        layout.addRow("Weekly Remaining", self.rate_limit_labels["secondary_remaining_percent"])
        layout.addRow("Source File", self.rate_limit_labels["file"])
        return group

    def _build_main_splitter(self) -> QSplitter:
        splitter = QSplitter(Qt.Orientation.Horizontal)

        self.thread_table = QTableWidget(0, len(THREAD_COLUMNS))
        self.thread_table.setHorizontalHeaderLabels([label for label, _ in THREAD_COLUMNS])
        self.thread_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.thread_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.thread_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.thread_table.setAlternatingRowColors(True)
        self.thread_table.setSortingEnabled(True)
        self.thread_table.horizontalHeader().setStretchLastSection(True)
        self.thread_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        splitter.addWidget(self.thread_table)

        self.details_text = QPlainTextEdit()
        self.details_text.setReadOnly(True)
        splitter.addWidget(self.details_text)
        splitter.setSizes([1000, 400])
        return splitter

    def refresh_report(self) -> None:
        days = self.days_spin.value()
        self.statusBar().showMessage(f"Refreshing report for last {days} day(s)...")

        try:
            report = load_report(days)
        except Exception as exc:
            QMessageBox.critical(self, "Refresh Failed", str(exc))
            self.statusBar().showMessage("Refresh failed")
            return

        self.current_report = report
        self.current_threads = report["threads"]
        self.populate_summary(report)
        self.populate_rate_limits(report.get("rate_limits"))
        self.populate_threads(self.current_threads)

        thread_count = report["active_thread_count"]
        self.statusBar().showMessage(f"Loaded {thread_count} active thread(s) for last {days} day(s).")

    def populate_summary(self, report: dict) -> None:
        summary = report["summary"]
        self.summary_labels["window_start"].setText(report["window_start"])
        self.summary_labels["window_end"].setText(report["window_end"])
        self.summary_labels["active_thread_count"].setText(str(report["active_thread_count"]))
        self.summary_labels["input_tokens"].setText(f"{summary['input_tokens']:,}")
        self.summary_labels["cached_input_tokens"].setText(f"{summary['cached_input_tokens']:,}")
        self.summary_labels["output_tokens"].setText(f"{summary['output_tokens']:,}")
        self.summary_labels["reasoning_output_tokens"].setText(f"{summary['reasoning_output_tokens']:,}")
        self.summary_labels["total_tokens"].setText(f"{summary['total_tokens']:,}")
        self.summary_labels["aggregate_cache_hit_rate"].setText(f"{summary['aggregate_cache_hit_rate']:.2f}%")

    def populate_rate_limits(self, rate_limits: dict | None) -> None:
        if not rate_limits:
            for label in self.rate_limit_labels.values():
                label.setText("No rate limits found")
            return

        self.rate_limit_labels["timestamp"].setText(rate_limits["timestamp"])
        self.rate_limit_labels["plan_type"].setText(str(rate_limits["plan_type"]))
        self.rate_limit_labels["primary_used_percent"].setText(f"{rate_limits['primary_used_percent']:.1f}%")
        self.rate_limit_labels["primary_remaining_percent"].setText(
            f"{rate_limits['primary_remaining_percent']:.1f}%"
        )
        self.rate_limit_labels["secondary_used_percent"].setText(f"{rate_limits['secondary_used_percent']:.1f}%")
        self.rate_limit_labels["secondary_remaining_percent"].setText(
            f"{rate_limits['secondary_remaining_percent']:.1f}%"
        )
        self.rate_limit_labels["file"].setText(rate_limits["file"])

    def populate_threads(self, threads: list[dict]) -> None:
        self.thread_table.setSortingEnabled(False)
        self.thread_table.clearContents()
        self.thread_table.setRowCount(len(threads))

        for row_index, thread in enumerate(threads):
            self._set_text_item(row_index, 0, thread["title"] or "(not found)")
            self._set_text_item(row_index, 1, thread["last_activity"] or "-")
            self._set_number_item(row_index, 2, thread["input_tokens"])
            self._set_number_item(row_index, 3, thread["cached_input_tokens"])
            self._set_number_item(row_index, 4, thread["output_tokens"])
            self._set_number_item(row_index, 5, thread["reasoning_output_tokens"])
            self._set_number_item(row_index, 6, thread["total_tokens"])
            self._set_float_item(row_index, 7, thread["cache_hit_rate"])
            self.thread_table.item(row_index, 0).setData(Qt.ItemDataRole.UserRole, thread)

        self.thread_table.setSortingEnabled(True)

        if threads:
            self.thread_table.selectRow(0)
        else:
            self.details_text.setPlainText("No active threads found for the selected window.")

    def update_details(self) -> None:
        selected_rows = self.thread_table.selectionModel().selectedRows()
        if not selected_rows:
            self.details_text.clear()
            return

        row_index = selected_rows[0].row()
        item = self.thread_table.item(row_index, 0)
        if item is None:
            self.details_text.clear()
            return

        thread = item.data(Qt.ItemDataRole.UserRole)
        if not thread:
            self.details_text.clear()
            return

        lines = [
            f"Title: {thread['title'] or '(not found)'}",
            f"Title Source: {thread['title_source']}",
            f"Thread ID: {thread['thread_id'] or '-'}",
            f"Last Activity: {thread['last_activity'] or '-'}",
            f"Latest Usage Timestamp: {thread['latest_usage_ts'] or '-'}",
            f"Input Tokens: {thread['input_tokens']:,}",
            f"Cached Input Tokens: {thread['cached_input_tokens']:,}",
            f"Output Tokens: {thread['output_tokens']:,}",
            f"Reasoning Output Tokens: {thread['reasoning_output_tokens']:,}",
            f"Total Tokens: {thread['total_tokens']:,}",
            f"Cache Hit Rate: {thread['cache_hit_rate']:.2f}%",
            f"Session File: {thread['file']}",
        ]
        self.details_text.setPlainText("\n".join(lines))

    def _set_text_item(self, row: int, col: int, text: str) -> None:
        item = QTableWidgetItem(text)
        item.setData(Qt.ItemDataRole.EditRole, text)
        self.thread_table.setItem(row, col, item)

    def _set_number_item(self, row: int, col: int, value: int, empty_if_zero: bool = False) -> None:
        text = "" if empty_if_zero and value == 0 else f"{value:,}"
        item = QTableWidgetItem(text)
        item.setData(Qt.ItemDataRole.EditRole, value)
        self.thread_table.setItem(row, col, item)

    def _set_float_item(self, row: int, col: int, value: float) -> None:
        item = QTableWidgetItem(f"{value:.2f}%")
        item.setData(Qt.ItemDataRole.EditRole, value)
        self.thread_table.setItem(row, col, item)


def run() -> int:
    app = QApplication.instance() or QApplication([])
    window = AnalyzerWindow()
    window.show()
    return app.exec()
