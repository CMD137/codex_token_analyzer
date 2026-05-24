from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QComboBox,
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

from analyzer_core import UTC, UTC_PLUS_8, load_report
from pricing import get_default_profile, load_pricing_config

UI_TEXT = {
    "zh": {
        "window_title": "Codex Token Analyzer",
        "language_label": "语言",
        "language_name": "中文",
        "window_days_label": "窗口天数",
        "days_tooltip": "选择要纳入统计的最近天数。",
        "refresh_button": "刷新",
        "summary_group": "汇总",
        "rate_limits_group": "额度",
        "summary_rows": {
            "window_start": "窗口开始",
            "window_end": "窗口结束",
            "active_thread_count": "活跃线程数",
            "input_tokens": "输入 token",
            "cached_input_tokens": "缓存输入 token",
            "output_tokens": "输出 token",
            "reasoning_output_tokens": "推理输出 token",
            "total_tokens": "总 token",
            "aggregate_cache_hit_rate": "整体缓存命中率",
            "estimated_cost_usd": "估算费用",
            "priced_thread_count": "已定价线程数",
            "unpriced_thread_count": "未定价线程数",
        },
        "rate_rows": {
            "timestamp": "时间",
            "plan_type": "套餐",
            "primary_used_percent": "5 小时已用",
            "primary_remaining_percent": "5 小时剩余",
            "secondary_used_percent": "周额度已用",
            "secondary_remaining_percent": "周额度剩余",
            "file": "来源文件",
        },
        "thread_columns": [
            "标题",
            "模型",
            "最近活动",
            "输入 token",
            "缓存输入 token",
            "输出 token",
            "推理输出 token",
            "总 token",
            "缓存命中率",
            "估算费用",
        ],
        "pricing_label": "定价档位",
        "status_ready": "就绪",
        "status_refreshing": "正在刷新最近 {days} 天的数据...",
        "status_loaded": "已加载最近 {days} 天的 {count} 个活跃线程。",
        "refresh_failed": "刷新失败",
        "no_rate_limits": "未找到额度信息",
        "no_active_threads": "所选时间窗口内没有活跃线程。",
        "details": {
            "title": "标题",
            "title_source": "标题来源",
            "thread_id": "线程 ID",
            "model": "模型",
            "last_activity": "最近活动",
            "latest_usage_ts": "最近用量时间",
            "input_tokens": "输入 token",
            "cached_input_tokens": "缓存输入 token",
            "output_tokens": "输出 token",
            "reasoning_output_tokens": "推理输出 token",
            "total_tokens": "总 token",
            "cache_hit_rate": "缓存命中率",
            "estimated_cost_usd": "估算费用",
            "file": "会话文件",
        },
        "not_found": "(未找到)",
        "cost_unavailable": "不可估算",
        "timezone": UTC_PLUS_8,
    },
    "en": {
        "window_title": "Codex Token Analyzer",
        "language_label": "Language",
        "language_name": "English",
        "window_days_label": "Window Days",
        "days_tooltip": "Choose how many recent days to include in the report.",
        "refresh_button": "Refresh",
        "summary_group": "Summary",
        "rate_limits_group": "Rate Limits",
        "summary_rows": {
            "window_start": "Window Start",
            "window_end": "Window End",
            "active_thread_count": "Active Threads",
            "input_tokens": "Input Tokens",
            "cached_input_tokens": "Cached Input",
            "output_tokens": "Output Tokens",
            "reasoning_output_tokens": "Reasoning Output",
            "total_tokens": "Total Tokens",
            "aggregate_cache_hit_rate": "Aggregate Cache Hit",
            "estimated_cost_usd": "Estimated Cost",
            "priced_thread_count": "Priced Threads",
            "unpriced_thread_count": "Unpriced Threads",
        },
        "rate_rows": {
            "timestamp": "Timestamp",
            "plan_type": "Plan",
            "primary_used_percent": "5h Used",
            "primary_remaining_percent": "5h Remaining",
            "secondary_used_percent": "Weekly Used",
            "secondary_remaining_percent": "Weekly Remaining",
            "file": "Source File",
        },
        "thread_columns": [
            "Title",
            "Model",
            "Last Activity",
            "Input",
            "Cached",
            "Output",
            "Reasoning",
            "Total",
            "Cache Hit %",
            "Est. Cost",
        ],
        "pricing_label": "Pricing",
        "status_ready": "Ready",
        "status_refreshing": "Refreshing report for last {days} day(s)...",
        "status_loaded": "Loaded {count} active thread(s) for last {days} day(s).",
        "refresh_failed": "Refresh Failed",
        "no_rate_limits": "No rate limits found",
        "no_active_threads": "No active threads found for the selected window.",
        "details": {
            "title": "Title",
            "title_source": "Title Source",
            "thread_id": "Thread ID",
            "model": "Model",
            "last_activity": "Last Activity",
            "latest_usage_ts": "Latest Usage Timestamp",
            "input_tokens": "Input Tokens",
            "cached_input_tokens": "Cached Input Tokens",
            "output_tokens": "Output Tokens",
            "reasoning_output_tokens": "Reasoning Output Tokens",
            "total_tokens": "Total Tokens",
            "cache_hit_rate": "Cache Hit Rate",
            "estimated_cost_usd": "Estimated Cost",
            "file": "Session File",
        },
        "not_found": "(not found)",
        "cost_unavailable": "unavailable",
        "timezone": UTC,
    },
}

THREAD_COLUMN_KEYS = [
    "title",
    "model",
    "last_activity",
    "input_tokens",
    "cached_input_tokens",
    "output_tokens",
    "reasoning_output_tokens",
    "total_tokens",
    "cache_hit_rate",
    "estimated_cost_usd",
]


class CostTableWidgetItem(QTableWidgetItem):
    def __init__(self, display_text: str, sort_value: float) -> None:
        super().__init__(display_text)
        self.sort_value = sort_value

    def __lt__(self, other: object) -> bool:
        if isinstance(other, CostTableWidgetItem):
            return self.sort_value < other.sort_value
        return super().__lt__(other)


class AnalyzerWindow(QMainWindow):
    def __init__(
        self,
        initial_language: str = "zh",
        pricing_config_path: str | None = None,
        initial_pricing_profile: str | None = None,
        initial_regional_pricing: bool = False,
    ) -> None:
        super().__init__()
        self.language = initial_language
        self.current_report: dict | None = None
        self.current_threads: list[dict] = []
        self.pricing_config_path = pricing_config_path
        self.pricing_config = load_pricing_config(pricing_config_path)

        self.resize(1400, 820)

        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)

        controls_layout = QHBoxLayout()
        self.language_label = QLabel()
        controls_layout.addWidget(self.language_label)

        self.language_combo = QComboBox()
        self.language_combo.addItem(UI_TEXT["zh"]["language_name"], "zh")
        self.language_combo.addItem(UI_TEXT["en"]["language_name"], "en")
        controls_layout.addWidget(self.language_combo)

        self.days_label = QLabel()
        controls_layout.addWidget(self.days_label)

        self.days_spin = QSpinBox()
        self.days_spin.setRange(1, 365)
        self.days_spin.setValue(7)
        controls_layout.addWidget(self.days_spin)

        self.pricing_label = QLabel()
        controls_layout.addWidget(self.pricing_label)

        self.pricing_combo = QComboBox()
        for profile_name in self.pricing_config["profiles"]:
            self.pricing_combo.addItem(profile_name, profile_name)
        default_profile = initial_pricing_profile or get_default_profile(self.pricing_config)
        self.pricing_combo.setCurrentIndex(self.pricing_combo.findData(default_profile))
        controls_layout.addWidget(self.pricing_combo)
        self.initial_regional_pricing = initial_regional_pricing

        self.refresh_button = QPushButton()
        controls_layout.addWidget(self.refresh_button)
        controls_layout.addStretch()
        root_layout.addLayout(controls_layout)

        top_panels_layout = QHBoxLayout()
        top_panels_layout.addWidget(self._build_summary_group(), 3)
        top_panels_layout.addWidget(self._build_rate_limits_group(), 2)
        root_layout.addLayout(top_panels_layout)
        root_layout.addWidget(self._build_main_splitter(), stretch=1)

        self.language_combo.currentIndexChanged.connect(self.change_language)
        self.pricing_combo.currentIndexChanged.connect(self.refresh_report)
        self.refresh_button.clicked.connect(self.refresh_report)
        self.days_spin.valueChanged.connect(self.refresh_report)
        self.thread_table.itemSelectionChanged.connect(self.update_details)

        self.summary_value_labels: dict[str, QLabel]
        self.rate_limit_value_labels: dict[str, QLabel]
        self.summary_caption_labels: dict[str, QLabel]
        self.rate_limit_caption_labels: dict[str, QLabel]

        language_index = self.language_combo.findData(initial_language)
        if language_index >= 0:
            self.language_combo.setCurrentIndex(language_index)

        self.apply_language()
        self.refresh_report()

    def _build_summary_group(self) -> QGroupBox:
        group = QGroupBox()
        layout = QGridLayout(group)

        self.summary_group = group
        self.summary_value_labels = {
            "window_start": QLabel("-"),
            "window_end": QLabel("-"),
            "active_thread_count": QLabel("-"),
            "input_tokens": QLabel("-"),
            "cached_input_tokens": QLabel("-"),
            "output_tokens": QLabel("-"),
            "reasoning_output_tokens": QLabel("-"),
            "total_tokens": QLabel("-"),
            "aggregate_cache_hit_rate": QLabel("-"),
            "estimated_cost_usd": QLabel("-"),
            "priced_thread_count": QLabel("-"),
            "unpriced_thread_count": QLabel("-"),
        }
        self.summary_caption_labels = {}
        summary_keys = [
            "window_start",
            "window_end",
            "active_thread_count",
            "input_tokens",
            "cached_input_tokens",
            "output_tokens",
            "reasoning_output_tokens",
            "total_tokens",
            "aggregate_cache_hit_rate",
            "estimated_cost_usd",
            "priced_thread_count",
            "unpriced_thread_count",
        ]

        for index, key in enumerate(summary_keys):
            row = index // 3
            col = (index % 3) * 2
            caption = QLabel()
            self.summary_caption_labels[key] = caption
            layout.addWidget(caption, row, col)
            layout.addWidget(self.summary_value_labels[key], row, col + 1)

        return group

    def _build_rate_limits_group(self) -> QGroupBox:
        group = QGroupBox()
        layout = QFormLayout(group)

        self.rate_limits_group = group
        self.rate_limit_value_labels = {
            "timestamp": QLabel("-"),
            "plan_type": QLabel("-"),
            "primary_used_percent": QLabel("-"),
            "primary_remaining_percent": QLabel("-"),
            "secondary_used_percent": QLabel("-"),
            "secondary_remaining_percent": QLabel("-"),
            "file": QLabel("-"),
        }
        self.rate_limit_caption_labels = {}
        rate_keys = [
            "timestamp",
            "plan_type",
            "primary_used_percent",
            "primary_remaining_percent",
            "secondary_used_percent",
            "secondary_remaining_percent",
        ]
        for key in rate_keys:
            caption = QLabel()
            self.rate_limit_caption_labels[key] = caption
            layout.addRow(caption, self.rate_limit_value_labels[key])
        return group

    def _build_main_splitter(self) -> QSplitter:
        splitter = QSplitter(Qt.Orientation.Horizontal)

        self.thread_table = QTableWidget(0, len(THREAD_COLUMN_KEYS))
        self.thread_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.thread_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.thread_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.thread_table.setAlternatingRowColors(True)
        self.thread_table.setSortingEnabled(True)
        self.thread_table.horizontalHeader().setStretchLastSection(True)
        self.thread_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
        self.thread_table.horizontalHeader().setSortIndicator(2, Qt.SortOrder.DescendingOrder)
        self.thread_table.setColumnWidth(0, 160)
        self.thread_table.setColumnWidth(1, 57)
        splitter.addWidget(self.thread_table)

        self.details_text = QPlainTextEdit()
        self.details_text.setReadOnly(True)
        splitter.addWidget(self.details_text)
        splitter.setSizes([1000, 400])
        return splitter

    def current_text(self) -> dict:
        return UI_TEXT[self.language]

    def apply_language(self) -> None:
        text = self.current_text()
        self.setWindowTitle(text["window_title"])
        self.language_label.setText(text["language_label"])
        self.days_label.setText(text["window_days_label"])
        self.days_spin.setToolTip(text["days_tooltip"])
        self.refresh_button.setText(text["refresh_button"])
        self.pricing_label.setText(text["pricing_label"])
        self.summary_group.setTitle(text["summary_group"])
        self.rate_limits_group.setTitle(text["rate_limits_group"])

        for key, caption in self.summary_caption_labels.items():
            caption.setText(text["summary_rows"][key])

        for key, caption in self.rate_limit_caption_labels.items():
            caption.setText(text["rate_rows"][key])

        self.thread_table.setHorizontalHeaderLabels(text["thread_columns"])
        self.statusBar().showMessage(text["status_ready"])

        if self.current_report is not None:
            self.populate_summary(self.current_report)
            self.populate_rate_limits(self.current_report.get("rate_limits"))
            self.populate_threads(self.current_threads)

    def change_language(self) -> None:
        self.language = self.language_combo.currentData()
        self.apply_language()
        self.refresh_report()

    def refresh_report(self) -> None:
        days = self.days_spin.value()
        text = self.current_text()
        self.statusBar().showMessage(text["status_refreshing"].format(days=days))

        try:
            self.pricing_config = load_pricing_config(self.pricing_config_path)
            current_profile = self.pricing_combo.currentData()
            self.pricing_combo.blockSignals(True)
            self.pricing_combo.clear()
            for profile_name in self.pricing_config["profiles"]:
                self.pricing_combo.addItem(profile_name, profile_name)
            selected_profile = current_profile if current_profile in self.pricing_config["profiles"] else get_default_profile(self.pricing_config)
            self.pricing_combo.setCurrentIndex(self.pricing_combo.findData(selected_profile))
            self.pricing_combo.blockSignals(False)
            report = load_report(
                days,
                display_timezone=text["timezone"],
                pricing_config_path=self.pricing_config_path,
                pricing_profile=self.pricing_combo.currentData(),
                regional_pricing=self.initial_regional_pricing,
            )
        except Exception as exc:
            QMessageBox.critical(self, text["refresh_failed"], str(exc))
            self.statusBar().showMessage(text["refresh_failed"])
            return

        self.current_report = report
        self.current_threads = report["threads"]
        self.populate_summary(report)
        self.populate_rate_limits(report.get("rate_limits"))
        self.populate_threads(self.current_threads)

        thread_count = report["active_thread_count"]
        self.statusBar().showMessage(text["status_loaded"].format(days=days, count=thread_count))

    def populate_summary(self, report: dict) -> None:
        labels = self.summary_value_labels
        summary = report["summary"]
        labels["window_start"].setText(report["window_start"])
        labels["window_end"].setText(report["window_end"])
        labels["active_thread_count"].setText(str(report["active_thread_count"]))
        labels["input_tokens"].setText(f"{summary['input_tokens']:,}")
        labels["cached_input_tokens"].setText(f"{summary['cached_input_tokens']:,}")
        labels["output_tokens"].setText(f"{summary['output_tokens']:,}")
        labels["reasoning_output_tokens"].setText(f"{summary['reasoning_output_tokens']:,}")
        labels["total_tokens"].setText(f"{summary['total_tokens']:,}")
        labels["aggregate_cache_hit_rate"].setText(f"{summary['aggregate_cache_hit_rate']:.2f}%")
        labels["estimated_cost_usd"].setText(self.format_cost(summary["estimated_cost_usd"]))
        labels["priced_thread_count"].setText(str(summary["priced_thread_count"]))
        labels["unpriced_thread_count"].setText(str(summary["unpriced_thread_count"]))

    def populate_rate_limits(self, rate_limits: dict | None) -> None:
        text = self.current_text()
        if not rate_limits:
            for label in self.rate_limit_value_labels.values():
                label.setText(text["no_rate_limits"])
            return

        self.rate_limit_value_labels["timestamp"].setText(rate_limits["timestamp"])
        self.rate_limit_value_labels["plan_type"].setText(str(rate_limits["plan_type"]))
        self.rate_limit_value_labels["primary_used_percent"].setText(f"{rate_limits['primary_used_percent']:.1f}%")
        self.rate_limit_value_labels["primary_remaining_percent"].setText(
            f"{rate_limits['primary_remaining_percent']:.1f}%"
        )
        self.rate_limit_value_labels["secondary_used_percent"].setText(
            f"{rate_limits['secondary_used_percent']:.1f}%"
        )
        self.rate_limit_value_labels["secondary_remaining_percent"].setText(
            f"{rate_limits['secondary_remaining_percent']:.1f}%"
        )
        self.rate_limit_value_labels["file"].setText(rate_limits["file"])

    def populate_threads(self, threads: list[dict]) -> None:
        text = self.current_text()
        self.thread_table.setSortingEnabled(False)
        self.thread_table.clearContents()
        self.thread_table.setRowCount(len(threads))

        for row_index, thread in enumerate(threads):
            self._set_text_item(row_index, 0, thread["title"] or text["not_found"])
            self._set_text_item(row_index, 1, thread["model"] or text["not_found"])
            self._set_text_item(row_index, 2, thread["last_activity"] or "-")
            self._set_number_item(row_index, 3, thread["input_tokens"])
            self._set_number_item(row_index, 4, thread["cached_input_tokens"])
            self._set_number_item(row_index, 5, thread["output_tokens"])
            self._set_number_item(row_index, 6, thread["reasoning_output_tokens"])
            self._set_number_item(row_index, 7, thread["total_tokens"])
            self._set_float_item(row_index, 8, thread["cache_hit_rate"])
            self._set_cost_item(row_index, 9, thread["estimated_cost_usd"], text["cost_unavailable"])
            self.thread_table.item(row_index, 0).setData(Qt.ItemDataRole.UserRole, thread)

        self.thread_table.setSortingEnabled(True)
        self.thread_table.sortItems(2, Qt.SortOrder.DescendingOrder)

        if threads:
            self.thread_table.selectRow(0)
        else:
            self.details_text.setPlainText(text["no_active_threads"])

    def update_details(self) -> None:
        text = self.current_text()
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
            f"{text['details']['title']}: {thread['title'] or text['not_found']}",
            f"{text['details']['title_source']}: {thread['title_source']}",
            f"{text['details']['thread_id']}: {thread['thread_id'] or '-'}",
            f"{text['details']['model']}: {thread['model'] or text['not_found']}",
            f"{text['details']['last_activity']}: {thread['last_activity'] or '-'}",
            f"{text['details']['latest_usage_ts']}: {thread['latest_usage_ts'] or '-'}",
            f"{text['details']['input_tokens']}: {thread['input_tokens']:,}",
            f"{text['details']['cached_input_tokens']}: {thread['cached_input_tokens']:,}",
            f"{text['details']['output_tokens']}: {thread['output_tokens']:,}",
            f"{text['details']['reasoning_output_tokens']}: {thread['reasoning_output_tokens']:,}",
            f"{text['details']['total_tokens']}: {thread['total_tokens']:,}",
            f"{text['details']['cache_hit_rate']}: {thread['cache_hit_rate']:.2f}%",
            f"{text['details']['estimated_cost_usd']}: {self.format_cost(thread['estimated_cost_usd'])}",
            f"{text['details']['file']}: {thread['file']}",
        ]
        self.details_text.setPlainText("\n".join(lines))

    def format_cost(self, value: float | None) -> str:
        if value is None:
            return self.current_text()["cost_unavailable"]
        return f"${value:,.4f}"

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

    def _set_cost_item(self, row: int, col: int, value: float | None, unavailable_text: str) -> None:
        if value is None:
            item = CostTableWidgetItem(unavailable_text, -1.0)
        else:
            item = CostTableWidgetItem(f"${value:,.4f}", value)
        self.thread_table.setItem(row, col, item)


def run(
    initial_language: str = "zh",
    pricing_config_path: str | None = None,
    initial_pricing_profile: str | None = None,
    initial_regional_pricing: bool = False,
) -> int:
    app = QApplication.instance() or QApplication([])
    window = AnalyzerWindow(
        initial_language=initial_language,
        pricing_config_path=pricing_config_path,
        initial_pricing_profile=initial_pricing_profile,
        initial_regional_pricing=initial_regional_pricing,
    )
    window.show()
    return app.exec()
