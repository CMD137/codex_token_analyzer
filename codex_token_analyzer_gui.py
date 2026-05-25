from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QComboBox,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QSplitter,
    QStyledItemDelegate,
    QStyle,
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
            "primary_reset_at": "5 小时重置于",
            "secondary_used_percent": "周额度已用",
            "secondary_remaining_percent": "周额度剩余",
            "secondary_reset_at": "周额度重置于",
            "source": "额度来源",
        },
        "thread_columns": [
            "标题",
            "模型",
            "最近活动时间",
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
            "message_round_count": "消息轮数",
            "avg_tokens_per_round": "平均每轮 token",
            "tool_call_count": "Tool Calls",
            "output_ratio": "Output Ratio",
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
            "primary_reset_at": "5h Resets At",
            "secondary_used_percent": "Weekly Used",
            "secondary_remaining_percent": "Weekly Remaining",
            "secondary_reset_at": "Weekly Resets At",
            "source": "Source",
        },
        "thread_columns": [
            "Title",
            "Model",
            "Last Activity Time",
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
            "message_round_count": "Message Rounds",
            "avg_tokens_per_round": "Avg Tokens / Round",
            "tool_call_count": "Tool Calls",
            "output_ratio": "Output Ratio",
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

DETAIL_FIELD_KEYS = [
    "title",
    "thread_id",
    "last_activity",
    "message_round_count",
    "avg_tokens_per_round",
    "tool_call_count",
    "output_ratio",
    "model",
    "latest_usage_ts",
    "input_tokens",
    "cached_input_tokens",
    "output_tokens",
    "reasoning_output_tokens",
    "total_tokens",
    "cache_hit_rate",
    "estimated_cost_usd",
    "title_source",
    "file",
]

COLOR_BG = "#0F1115"
COLOR_PANEL = "#151821"
COLOR_CARD = "#1B1F2A"
COLOR_HEADER = "#12151C"
COLOR_ROW_ODD = "#1A1D24"
COLOR_ROW_EVEN = "#20242D"
COLOR_TEXT_PRIMARY = "#F2F5FA"
COLOR_TEXT_BODY = "#D6DAE3"
COLOR_TEXT_SECONDARY = "#8E96A8"
COLOR_TEXT_MUTED = "#6F7788"
COLOR_BORDER = "rgba(255, 255, 255, 0.08)"
COLOR_BORDER_STRONG = "rgba(255, 255, 255, 0.14)"
COLOR_PRIMARY = "#3B82F6"
COLOR_PRIMARY_HOVER = "#60A5FA"
COLOR_PRIMARY_SELECTED_BG = "rgba(59, 130, 246, 0.22)"
COLOR_PRIMARY_SELECTED_BORDER = "rgba(96, 165, 250, 0.55)"
COLOR_SUCCESS = "#22C55E"
COLOR_WARNING = "#F59E0B"
COLOR_DANGER = "#EF4444"
COLOR_NEUTRAL = "#64748B"


def format_short_number(value: int | float) -> str:
    absolute = abs(float(value))
    if absolute >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    if absolute >= 1_000:
        return f"{value / 1_000:.1f}K"
    return f"{int(value)}"


def format_token_table_number(value: int | float) -> str:
    absolute = abs(float(value))
    if absolute >= 1_000_000:
        return f"{value / 1_000_000:.3f}M"
    return f"{value / 1_000:.3f}K"


def metric_color(value: float, *, high_good: bool, warn_threshold: float, good_threshold: float) -> str:
    if high_good:
        if value >= good_threshold:
            return COLOR_SUCCESS
        if value >= warn_threshold:
            return COLOR_WARNING
        return COLOR_DANGER

    if value < warn_threshold:
        return COLOR_SUCCESS
    if value < good_threshold:
        return COLOR_WARNING
    return COLOR_DANGER


def metric_status(value: float, *, high_good: bool, warn_threshold: float, good_threshold: float) -> str:
    if high_good:
        if value >= good_threshold:
            return "good"
        if value >= warn_threshold:
            return "warning"
        return "danger"

    if value < warn_threshold:
        return "good"
    if value < good_threshold:
        return "warning"
    return "danger"


class CostTableWidgetItem(QTableWidgetItem):
    def __init__(self, display_text: str, sort_value: float) -> None:
        super().__init__(display_text)
        self.sort_value = sort_value

    def __lt__(self, other: object) -> bool:
        if isinstance(other, CostTableWidgetItem):
            return self.sort_value < other.sort_value
        return super().__lt__(other)


class NumericTableWidgetItem(QTableWidgetItem):
    def __init__(self, display_text: str, sort_value: int | float) -> None:
        super().__init__(display_text)
        self.sort_value = float(sort_value)

    def __lt__(self, other: object) -> bool:
        if isinstance(other, NumericTableWidgetItem):
            return self.sort_value < other.sort_value
        if isinstance(other, CostTableWidgetItem):
            return self.sort_value < other.sort_value
        return super().__lt__(other)


class NoFocusDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index) -> None:
        option.state &= ~QStyle.StateFlag.State_HasFocus
        super().paint(painter, option, index)


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
        central.setObjectName("appRoot")
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(16, 16, 16, 16)
        root_layout.setSpacing(12)

        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)
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

        root_layout.addWidget(self._build_summary_group())
        root_layout.addWidget(self._build_main_splitter(), stretch=1)

        self.language_combo.currentIndexChanged.connect(self.change_language)
        self.pricing_combo.currentIndexChanged.connect(self.refresh_report)
        self.refresh_button.clicked.connect(self.refresh_report)
        self.days_spin.valueChanged.connect(self.refresh_report)
        self.thread_table.itemSelectionChanged.connect(self.update_details)

        self.summary_value_labels: dict[str, QLabel]
        self.rate_limit_value_labels: dict[str, QLabel] = {}
        self.rate_limit_caption_labels: dict[str, QLabel] = {}

        language_index = self.language_combo.findData(initial_language)
        if language_index >= 0:
            self.language_combo.setCurrentIndex(language_index)

        self._apply_theme()
        self.apply_language()
        self.refresh_report()

    def _apply_theme(self) -> None:
        self.setStyleSheet(
            f"""
            QMainWindow {{
                background: {COLOR_BG};
            }}
            QWidget#appRoot {{
                background: {COLOR_BG};
            }}
            QLabel {{
                color: {COLOR_TEXT_BODY};
                background: transparent;
            }}
            QStatusBar {{
                background: {COLOR_BG};
                color: {COLOR_TEXT_SECONDARY};
                border-top: 1px solid {COLOR_BORDER};
            }}
            QComboBox, QSpinBox, QPushButton {{
                min-height: 34px;
                padding: 0 12px;
                color: {COLOR_TEXT_BODY};
                background: {COLOR_CARD};
                border: 1px solid {COLOR_BORDER};
                border-radius: 10px;
            }}
            QComboBox:hover, QSpinBox:hover, QPushButton:hover {{
                border: 1px solid {COLOR_BORDER_STRONG};
                background: #202533;
            }}
            QComboBox:focus, QSpinBox:focus, QPushButton:focus {{
                border: 1px solid {COLOR_PRIMARY_SELECTED_BORDER};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QAbstractItemView {{
                background: {COLOR_CARD};
                color: {COLOR_TEXT_BODY};
                selection-background-color: {COLOR_PRIMARY_SELECTED_BG};
                border: 1px solid {COLOR_BORDER};
            }}
            QSplitter::handle {{
                background: {COLOR_BG};
                width: 8px;
            }}
            QTableWidget {{
                background: {COLOR_ROW_ODD};
                alternate-background-color: {COLOR_ROW_EVEN};
                color: {COLOR_TEXT_BODY};
                gridline-color: rgba(255, 255, 255, 0.06);
                border: 1px solid {COLOR_BORDER};
                border-radius: 12px;
                selection-background-color: transparent;
            }}
            QHeaderView::section {{
                background: {COLOR_HEADER};
                color: {COLOR_TEXT_SECONDARY};
                border: none;
                border-right: 1px solid rgba(255, 255, 255, 0.06);
                border-bottom: 1px solid rgba(255, 255, 255, 0.06);
                padding: 10px 8px;
                font-weight: 600;
            }}
            QTableCornerButton::section {{
                background: {COLOR_HEADER};
                border: none;
                border-right: 1px solid rgba(255, 255, 255, 0.06);
                border-bottom: 1px solid rgba(255, 255, 255, 0.06);
            }}
            QTableWidget::item {{
                padding: 8px 10px;
                border: none;
            }}
            QTableWidget::item:hover {{
                background: rgba(59, 130, 246, 0.12);
            }}
            QTableWidget::item:selected {{
                background: rgba(59, 130, 246, 0.28);
            }}
            QPlainTextEdit {{
                background: {COLOR_PANEL};
                color: {COLOR_TEXT_BODY};
                border: 1px solid {COLOR_BORDER};
                border-radius: 12px;
                padding: 12px;
                selection-background-color: {COLOR_PRIMARY_SELECTED_BG};
            }}
            QFrame#detailsPanel {{
                background: {COLOR_PANEL};
                border: 1px solid {COLOR_BORDER};
                border-radius: 12px;
            }}
            QLabel[role="detailTitle"] {{
                color: {COLOR_TEXT_SECONDARY};
                font-size: 12px;
                font-weight: 600;
                letter-spacing: 0.3px;
            }}
            QLabel[role="detailKey"] {{
                color: {COLOR_TEXT_SECONDARY};
                font-size: 12px;
            }}
            QLabel[role="detailValue"] {{
                color: {COLOR_TEXT_PRIMARY};
                font-size: 13px;
                font-weight: 500;
            }}
            QLabel[role="detailEmpty"] {{
                color: {COLOR_TEXT_MUTED};
                font-size: 13px;
            }}
            QScrollArea#detailsScroll {{
                border: none;
                background: transparent;
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 10px;
                margin: 8px 2px 8px 2px;
            }}
            QScrollBar::handle:vertical {{
                background: rgba(255, 255, 255, 0.18);
                border-radius: 5px;
                min-height: 24px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
            }}
            """
        )

    def _build_summary_group(self) -> QGroupBox:
        group = QGroupBox()
        self.summary_group = group
        group.setObjectName("summaryGroup")
        group.setStyleSheet(
            """
            QGroupBox#summaryGroup {
                background: #151821;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 12px;
                margin-top: 10px;
                padding: 8px;
            }
            QGroupBox#summaryGroup::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 4px;
                color: #8E96A8;
            }
            QFrame[cardRole="kpi"] {
                background: #1B1F2A;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 12px;
            }
            QFrame[cardRole="kpi"]:hover {
                background: #202533;
                border: 1px solid rgba(255, 255, 255, 0.14);
            }
            QFrame[cardRole="kpi"][status="warning"] {
                background: rgba(245, 158, 11, 0.08);
                border: 1px solid rgba(245, 158, 11, 0.30);
            }
            QFrame[cardRole="kpi"][status="danger"] {
                background: rgba(239, 68, 68, 0.08);
                border: 1px solid rgba(239, 68, 68, 0.35);
            }
            QFrame[cardRole="metric"] {
                background: #1B1F2A;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 10px;
            }
            QFrame[cardRole="metric"]:hover {
                background: #202533;
                border: 1px solid rgba(255, 255, 255, 0.14);
            }
            QLabel[role="sectionTitle"] {
                color: #8E96A8;
                font-size: 12px;
                font-weight: 600;
                letter-spacing: 0.4px;
            }
            QLabel[role="kpiLabel"] {
                color: #8E96A8;
                font-size: 13px;
            }
            QLabel[role="kpiValue"] {
                color: #F2F5FA;
                font-size: 30px;
                font-weight: 700;
            }
            QLabel[role="metricLabel"] {
                color: #8E96A8;
                font-size: 11px;
            }
            QLabel[role="metricValue"] {
                color: #F2F5FA;
                font-size: 18px;
                font-weight: 600;
            }
            QLabel[role="contextValue"] {
                color: #D6DAE3;
                font-size: 14px;
                font-weight: 500;
            }
            QProgressBar {
                border: none;
                border-radius: 5px;
                background: rgba(255, 255, 255, 0.08);
                height: 8px;
                text-align: center;
            }
            QProgressBar::chunk {
                border-radius: 5px;
            }
            """
        )

        outer_layout = QVBoxLayout(group)
        outer_layout.setContentsMargins(12, 16, 12, 12)
        outer_layout.setSpacing(10)

        self.summary_sections = {
            "core": QLabel(),
            "tokens": QLabel(),
            "context": QLabel(),
        }
        for label in self.summary_sections.values():
            label.setProperty("role", "sectionTitle")

        self.kpi_labels: dict[str, QLabel] = {}
        self.summary_value_labels = {}
        self.kpi_subtitles: dict[str, QLabel] = {}
        self.kpi_progress_bars: dict[str, QProgressBar] = {}
        self.kpi_cards: dict[str, QFrame] = {}

        outer_layout.addWidget(self.summary_sections["core"])
        core_layout = QHBoxLayout()
        core_layout.setSpacing(10)
        for key in ("estimated_cost_usd", "total_tokens", "primary_remaining_percent", "secondary_remaining_percent"):
            frame = self._build_kpi_card(key)
            core_layout.addWidget(frame, 1)
        outer_layout.addLayout(core_layout)

        outer_layout.addWidget(self.summary_sections["tokens"])
        token_layout = QHBoxLayout()
        token_layout.setSpacing(10)
        for key in ("input_tokens", "cached_input_tokens", "output_tokens", "reasoning_output_tokens"):
            token_layout.addWidget(self._build_metric_card(key, value_role="metricValue"), 1)
        outer_layout.addLayout(token_layout)

        outer_layout.addWidget(self.summary_sections["context"])
        context_layout = QHBoxLayout()
        context_layout.setSpacing(10)
        for key in ("aggregate_cache_hit_rate", "active_thread_count", "priced_thread_count", "unpriced_thread_count"):
            context_layout.addWidget(self._build_metric_card(key, value_role="contextValue"), 1)
        outer_layout.addLayout(context_layout)

        return group

    def _build_kpi_card(self, key: str) -> QFrame:
        frame = QFrame()
        frame.setProperty("cardRole", "kpi")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(6)

        label = QLabel()
        label.setProperty("role", "kpiLabel")
        value = QLabel("-")
        value.setProperty("role", "kpiValue")
        subtitle = QLabel("")
        subtitle.setProperty("role", "metricLabel")
        progress = QProgressBar()
        progress.setRange(0, 100)
        progress.setTextVisible(False)
        progress.hide()

        layout.addWidget(label)
        layout.addWidget(value)
        layout.addWidget(subtitle)
        layout.addWidget(progress)
        layout.addStretch()

        self.kpi_cards[key] = frame
        self.kpi_labels[key] = label
        self.summary_value_labels[key] = value
        self.kpi_subtitles[key] = subtitle
        self.kpi_progress_bars[key] = progress
        return frame

    def _build_metric_card(self, key: str, *, value_role: str) -> QFrame:
        frame = QFrame()
        frame.setProperty("cardRole", "metric")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(4)

        label = QLabel()
        label.setProperty("role", "metricLabel")
        value = QLabel("-")
        value.setProperty("role", value_role)

        layout.addWidget(label)
        layout.addWidget(value)
        layout.addStretch()

        self.kpi_labels[key] = label
        self.summary_value_labels[key] = value
        return frame

    def _build_main_splitter(self) -> QSplitter:
        splitter = QSplitter(Qt.Orientation.Horizontal)

        self.thread_table = QTableWidget(0, len(THREAD_COLUMN_KEYS))
        self.thread_table.setItemDelegate(NoFocusDelegate(self.thread_table))
        self.thread_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.thread_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.thread_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.thread_table.setAlternatingRowColors(True)
        self.thread_table.setSortingEnabled(True)
        self.thread_table.horizontalHeader().setStretchLastSection(True)
        self.thread_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
        self.thread_table.horizontalHeader().setSortIndicator(2, Qt.SortOrder.DescendingOrder)
        self.thread_table.setColumnWidth(0, 160)
        self.thread_table.setColumnWidth(1, 86)
        self.thread_table.setColumnWidth(2, 220)
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
        self.summary_sections["core"].setText("Results")
        self.summary_sections["tokens"].setText("Token Breakdown")
        self.summary_sections["context"].setText("Runtime Context")
        if self.language == "zh":
            self.summary_sections["core"].setText("核心 KPI")
            self.summary_sections["tokens"].setText("Token 构成")
            self.summary_sections["context"].setText("运行上下文")

        if self.language == "zh":
            self.summary_sections["core"].setText("\u7ed3\u679c")
            self.summary_sections["tokens"].setText("Token \u6784\u6210")
            self.summary_sections["context"].setText("\u8fd0\u884c\u4e0a\u4e0b\u6587")

        for key, caption in self.kpi_labels.items():
            if key == "time_window":
                caption.setText("时间窗口" if self.language == "zh" else "Time Window")
            elif key == "primary_used_percent":
                caption.setText("5 小时额度已用" if self.language == "zh" else "5h Used")
            else:
                caption.setText(text["summary_rows"].get(key, key))

        for key, caption in self.rate_limit_caption_labels.items():
            caption.setText(text["rate_rows"][key])

        for key, caption in self.kpi_labels.items():
            if key == "primary_remaining_percent":
                caption.setText("5 \u5c0f\u65f6\u989d\u5ea6" if self.language == "zh" else "5h Limit")
            elif key == "secondary_remaining_percent":
                caption.setText("\u5468\u989d\u5ea6" if self.language == "zh" else "Weekly Limit")

        self.thread_table.setHorizontalHeaderLabels(text["thread_columns"])
        self.statusBar().showMessage(text["status_ready"])

        if self.current_report is not None:
            self.populate_summary(self.current_report)
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
        self.populate_threads(self.current_threads)

        thread_count = report["active_thread_count"]
        self.statusBar().showMessage(text["status_loaded"].format(days=days, count=thread_count))

    def populate_summary(self, report: dict) -> None:
        labels = self.summary_value_labels
        summary = report["summary"]
        rate_limits = report.get("rate_limits") or {}
        total_tokens = summary["total_tokens"]
        cache_hit_rate = summary["aggregate_cache_hit_rate"]
        primary_used = rate_limits.get("primary_used_percent")

        labels["estimated_cost_usd"].setText(self.format_cost_compact(summary["estimated_cost_usd"]))
        labels["estimated_cost_usd"].setToolTip(self.format_cost(summary["estimated_cost_usd"]))
        self.kpi_subtitles["estimated_cost_usd"].setText("参考：developers.openai.com/api/docs/pricing")

        labels["total_tokens"].setText(format_short_number(total_tokens))
        labels["total_tokens"].setToolTip(f"{total_tokens:,}")
        self.kpi_subtitles["total_tokens"].setText(report["timezone_label"])

        labels["aggregate_cache_hit_rate"].setText(f"{cache_hit_rate:.1f}%")
        labels["aggregate_cache_hit_rate"].setToolTip(f"{cache_hit_rate:.2f}%")
        cache_color = metric_color(cache_hit_rate, high_good=True, warn_threshold=70.0, good_threshold=85.0)
        labels["aggregate_cache_hit_rate"].setStyleSheet(f"color: {cache_color}; font-size: 28px; font-weight: 700;")
        self.kpi_subtitles["aggregate_cache_hit_rate"].setText(
            "cached / input" if self.language == "en" else "cached input / input"
        )

        if primary_used is None:
            labels["primary_used_percent"].setText("-")
            self.kpi_subtitles["primary_used_percent"].setText(self.current_text()["no_rate_limits"])
            self.kpi_progress_bars["primary_used_percent"].hide()
        else:
            labels["primary_used_percent"].setText(f"{primary_used:.0f}%")
            labels["primary_used_percent"].setToolTip(f"{primary_used:.1f}%")
            remaining = rate_limits.get("primary_remaining_percent", max(0.0, 100.0 - primary_used))
            self.kpi_subtitles["primary_used_percent"].setText(
                (f"remaining {remaining:.0f}%" if self.language == "en" else f"剩余 {remaining:.0f}%")
            )
            progress = self.kpi_progress_bars["primary_used_percent"]
            progress.setValue(int(round(primary_used)))
            progress.setStyleSheet(
                "QProgressBar{border:none;border-radius:4px;background:rgba(255,255,255,0.08);height:8px;}"
                f"QProgressBar::chunk{{border-radius:4px;background:{metric_color(primary_used, high_good=False, warn_threshold=70.0, good_threshold=90.0)};}}"
            )
            progress.show()

        for key in ("input_tokens", "cached_input_tokens", "output_tokens", "reasoning_output_tokens"):
            value = summary[key]
            labels[key].setText(format_short_number(value))
            labels[key].setToolTip(f"{value:,}")

        window_tooltip = f"{report['window_start']} -> {report['window_end']}"
        if self.language == "en":
            window_text = f"Last {report['window_days']} days · {report['timezone_label']}"
        else:
            window_text = f"最近 {report['window_days']} 天 · {report['timezone_label']}"
        labels["time_window"].setText(window_text)
        labels["time_window"].setToolTip(window_tooltip)
        labels["active_thread_count"].setText(str(report["active_thread_count"]))
        labels["active_thread_count"].setToolTip(str(report["active_thread_count"]))
        labels["priced_thread_count"].setText(str(summary["priced_thread_count"]))
        labels["priced_thread_count"].setToolTip(str(summary["priced_thread_count"]))
        labels["unpriced_thread_count"].setText(str(summary["unpriced_thread_count"]))
        labels["unpriced_thread_count"].setToolTip(str(summary["unpriced_thread_count"]))

        # Reset styles for non-colored KPI values when language/theme is refreshed.
        for key in ("estimated_cost_usd", "total_tokens", "primary_used_percent"):
            labels[key].setStyleSheet("color: #F5F7FA; font-size: 28px; font-weight: 700;")

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
        self.rate_limit_value_labels["primary_reset_at"].setText(
            rate_limits.get("primary_reset_at") or "-"
        )
        self.rate_limit_value_labels["secondary_used_percent"].setText(
            f"{rate_limits['secondary_used_percent']:.1f}%"
        )
        self.rate_limit_value_labels["secondary_remaining_percent"].setText(
            f"{rate_limits['secondary_remaining_percent']:.1f}%"
        )
        self.rate_limit_value_labels["secondary_reset_at"].setText(
            rate_limits.get("secondary_reset_at") or "-"
        )
        self.rate_limit_value_labels["source"].setText(rate_limits["source"])

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

    def format_cost_compact(self, value: float | None) -> str:
        if value is None:
            return self.current_text()["cost_unavailable"]
        return f"${value:,.2f}"

    def _set_text_item(self, row: int, col: int, text: str) -> None:
        item = QTableWidgetItem(text)
        item.setData(Qt.ItemDataRole.EditRole, text)
        self.thread_table.setItem(row, col, item)

    def _set_number_item(self, row: int, col: int, value: int, empty_if_zero: bool = False) -> None:
        text = "" if empty_if_zero and value == 0 else f"{value:,}"
        item = NumericTableWidgetItem(text, value)
        self.thread_table.setItem(row, col, item)

    def _set_float_item(self, row: int, col: int, value: float) -> None:
        item = NumericTableWidgetItem(f"{value:.2f}%", value)
        self.thread_table.setItem(row, col, item)

    def _set_cost_item(self, row: int, col: int, value: float | None, unavailable_text: str) -> None:
        if value is None:
            item = CostTableWidgetItem(unavailable_text, -1.0)
        else:
            item = CostTableWidgetItem(f"${value:,.4f}", value)
        self.thread_table.setItem(row, col, item)

    def apply_language(self) -> None:
        text = self.current_text()
        self.setWindowTitle(text["window_title"])
        self.language_label.setText(text["language_label"])
        self.days_label.setText(text["window_days_label"])
        self.days_spin.setToolTip(text["days_tooltip"])
        self.refresh_button.setText(text["refresh_button"])
        self.pricing_label.setText(text["pricing_label"])
        self.summary_group.setTitle(text["summary_group"])
        self.summary_sections["core"].setText("Results")
        self.summary_sections["tokens"].setText("Token Breakdown")
        self.summary_sections["context"].setText("Runtime Context")
        if self.language == "zh":
            self.summary_sections["core"].setText("\u7ed3\u679c")
            self.summary_sections["tokens"].setText("Token \u6784\u6210")
            self.summary_sections["context"].setText("\u8fd0\u884c\u4e0a\u4e0b\u6587")

        for key, caption in self.kpi_labels.items():
            if key == "primary_remaining_percent":
                caption.setText("5 \u5c0f\u65f6\u989d\u5ea6" if self.language == "zh" else "5h Limit")
            elif key == "secondary_remaining_percent":
                caption.setText("\u5468\u989d\u5ea6" if self.language == "zh" else "Weekly Limit")
            else:
                caption.setText(text["summary_rows"].get(key, key))

        self.thread_table.setHorizontalHeaderLabels(text["thread_columns"])
        self.statusBar().showMessage(text["status_ready"])

        if self.current_report is not None:
            self.populate_summary(self.current_report)
            self.populate_threads(self.current_threads)

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
            selected_profile = (
                current_profile
                if current_profile in self.pricing_config["profiles"]
                else get_default_profile(self.pricing_config)
            )
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
        self.populate_threads(self.current_threads)

        thread_count = report["active_thread_count"]
        self.statusBar().showMessage(text["status_loaded"].format(days=days, count=thread_count))

    def populate_summary(self, report: dict) -> None:
        labels = self.summary_value_labels
        summary = report["summary"]
        rate_limits = report.get("rate_limits") or {}
        total_tokens = summary["total_tokens"]
        cache_hit_rate = summary["aggregate_cache_hit_rate"]

        labels["estimated_cost_usd"].setText(self.format_cost_compact(summary["estimated_cost_usd"]))
        labels["estimated_cost_usd"].setToolTip(self.format_cost(summary["estimated_cost_usd"]))
        self.kpi_subtitles["estimated_cost_usd"].setText("参考：developers.openai.com/api/docs/pricing")
        labels["estimated_cost_usd"].setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-size: 45px; font-weight: 700;")
        self._set_kpi_state("estimated_cost_usd", "neutral")

        labels["total_tokens"].setText(format_short_number(total_tokens))
        labels["total_tokens"].setToolTip(f"{total_tokens:,}")
        self.kpi_subtitles["total_tokens"].setText("")
        labels["total_tokens"].setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-size: 45px; font-weight: 700;")
        self._set_kpi_state("total_tokens", "neutral")

        labels["aggregate_cache_hit_rate"].setText(f"{cache_hit_rate:.1f}%")
        labels["aggregate_cache_hit_rate"].setToolTip(f"{cache_hit_rate:.2f}%")
        labels["aggregate_cache_hit_rate"].setStyleSheet(
            f"color: {metric_color(cache_hit_rate, high_good=True, warn_threshold=70.0, good_threshold=85.0)};"
            "font-size: 14px; font-weight: 600;"
        )

        for key in ("input_tokens", "cached_input_tokens", "output_tokens", "reasoning_output_tokens"):
            value = summary[key]
            labels[key].setText(format_short_number(value))
            labels[key].setToolTip(f"{value:,}")

        labels["active_thread_count"].setText(str(report["active_thread_count"]))
        labels["active_thread_count"].setToolTip(str(report["active_thread_count"]))
        labels["priced_thread_count"].setText(str(summary["priced_thread_count"]))
        labels["priced_thread_count"].setToolTip(str(summary["priced_thread_count"]))
        labels["unpriced_thread_count"].setText(str(summary["unpriced_thread_count"]))
        labels["unpriced_thread_count"].setToolTip(str(summary["unpriced_thread_count"]))

        self._populate_limit_kpi(
            key="primary_remaining_percent",
            remaining_percent=rate_limits.get("primary_remaining_percent"),
            reset_at=rate_limits.get("primary_reset_at"),
            fallback_text=self.current_text()["no_rate_limits"],
        )
        self._populate_limit_kpi(
            key="secondary_remaining_percent",
            remaining_percent=rate_limits.get("secondary_remaining_percent"),
            reset_at=rate_limits.get("secondary_reset_at"),
            fallback_text=self.current_text()["no_rate_limits"],
        )

    def populate_threads(self, threads: list[dict]) -> None:
        text = self.current_text()
        self.thread_table.setSortingEnabled(False)
        self.thread_table.clearContents()
        self.thread_table.setRowCount(len(threads))

        for row_index, thread in enumerate(threads):
            self._set_text_item(row_index, 0, thread["title"] or text["not_found"])
            self._set_text_item(row_index, 1, thread["model"] or text["not_found"])
            self._set_text_item(row_index, 2, thread["last_activity"] or "-")
            self._set_token_item(row_index, 3, thread["input_tokens"])
            self._set_token_item(row_index, 4, thread["cached_input_tokens"])
            self._set_token_item(row_index, 5, thread["output_tokens"])
            self._set_token_item(row_index, 6, thread["reasoning_output_tokens"])
            self._set_token_item(row_index, 7, thread["total_tokens"])
            self._set_float_item(row_index, 8, thread["cache_hit_rate"])
            self._set_cost_item(row_index, 9, thread["estimated_cost_usd"], text["cost_unavailable"])
            self.thread_table.item(row_index, 0).setData(Qt.ItemDataRole.UserRole, thread)

        self.thread_table.setSortingEnabled(True)
        self.thread_table.sortItems(2, Qt.SortOrder.DescendingOrder)

        if threads:
            self.thread_table.selectRow(0)
        else:
            self.details_text.setPlainText(text["no_active_threads"])

    def _set_token_item(self, row: int, col: int, value: int) -> None:
        item = NumericTableWidgetItem(format_token_table_number(value), value)
        item.setToolTip(f"{value:,}")
        self.thread_table.setItem(row, col, item)

    def _populate_limit_kpi(
        self,
        *,
        key: str,
        remaining_percent: float | None,
        reset_at: str | None,
        fallback_text: str,
    ) -> None:
        value_label = self.summary_value_labels[key]
        subtitle_label = self.kpi_subtitles[key]
        progress = self.kpi_progress_bars[key]

        if remaining_percent is None:
            value_label.setText("-")
            value_label.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-size: 30px; font-weight: 700;")
            subtitle_label.setText(fallback_text)
            progress.hide()
            self._set_kpi_state(key, "neutral")
            return

        color = metric_color(remaining_percent, high_good=True, warn_threshold=20.0, good_threshold=50.0)
        status = metric_status(remaining_percent, high_good=True, warn_threshold=20.0, good_threshold=50.0)
        prefix = "Remaining" if self.language == "en" else "\u5269\u4f59"
        reset_prefix = "Next reset" if self.language == "en" else "\u4e0b\u6b21\u91cd\u7f6e"

        value_label.setText(f"{prefix} {remaining_percent:.0f}%")
        value_label.setToolTip(f"{remaining_percent:.1f}%")
        value_label.setStyleSheet(f"color: {color}; font-size: 30px; font-weight: 700;")
        subtitle_label.setText(f"{reset_prefix} {reset_at or '-'}")
        progress.setValue(int(round(remaining_percent)))
        progress.setStyleSheet(
            "QProgressBar{border:none;border-radius:5px;background:rgba(255,255,255,0.08);height:8px;}"
            f"QProgressBar::chunk{{border-radius:5px;background:{color};}}"
        )
        progress.show()
        self._set_kpi_state(key, status)

    def _set_kpi_state(self, key: str, status: str) -> None:
        frame = self.kpi_cards[key]
        frame.setProperty("status", status)
        frame.style().unpolish(frame)
        frame.style().polish(frame)
        frame.update()

    def _build_main_splitter(self) -> QSplitter:
        splitter = QSplitter(Qt.Orientation.Horizontal)

        self.thread_table = QTableWidget(0, len(THREAD_COLUMN_KEYS))
        self.thread_table.setItemDelegate(NoFocusDelegate(self.thread_table))
        self.thread_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.thread_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.thread_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.thread_table.setAlternatingRowColors(True)
        self.thread_table.setSortingEnabled(True)
        self.thread_table.horizontalHeader().setStretchLastSection(True)
        self.thread_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
        self.thread_table.horizontalHeader().setSortIndicator(2, Qt.SortOrder.DescendingOrder)
        self.thread_table.setColumnWidth(0, 160)
        self.thread_table.setColumnWidth(1, 86)
        self.thread_table.setColumnWidth(2, 220)
        splitter.addWidget(self.thread_table)

        details_panel = QFrame()
        details_panel.setObjectName("detailsPanel")
        details_layout = QVBoxLayout(details_panel)
        details_layout.setContentsMargins(14, 14, 14, 14)
        details_layout.setSpacing(10)

        self.details_title_label = QLabel()
        self.details_title_label.setProperty("role", "detailTitle")
        details_layout.addWidget(self.details_title_label)

        self.details_empty_label = QLabel()
        self.details_empty_label.setProperty("role", "detailEmpty")
        self.details_empty_label.setWordWrap(True)
        details_layout.addWidget(self.details_empty_label)

        self.details_scroll = QScrollArea()
        self.details_scroll.setObjectName("detailsScroll")
        self.details_scroll.setWidgetResizable(True)

        details_content = QWidget()
        self.details_grid = QGridLayout(details_content)
        self.details_grid.setContentsMargins(0, 0, 0, 0)
        self.details_grid.setHorizontalSpacing(12)
        self.details_grid.setVerticalSpacing(8)
        self.details_grid.setColumnStretch(1, 1)

        self.detail_caption_labels = {}
        self.detail_value_labels = {}
        for row_index, key in enumerate(DETAIL_FIELD_KEYS):
            caption = QLabel()
            caption.setProperty("role", "detailKey")
            caption.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

            value = QLabel("-")
            value.setProperty("role", "detailValue")
            value.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
            value.setWordWrap(True)
            value.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

            self.details_grid.addWidget(caption, row_index, 0)
            self.details_grid.addWidget(value, row_index, 1)
            self.detail_caption_labels[key] = caption
            self.detail_value_labels[key] = value

        self.details_scroll.setWidget(details_content)
        details_layout.addWidget(self.details_scroll, 1)
        splitter.addWidget(details_panel)
        splitter.setSizes([1000, 400])
        return splitter

    def apply_language(self) -> None:
        text = self.current_text()
        self.setWindowTitle(text["window_title"])
        self.language_label.setText(text["language_label"])
        self.days_label.setText(text["window_days_label"])
        self.days_spin.setToolTip(text["days_tooltip"])
        self.refresh_button.setText(text["refresh_button"])
        self.pricing_label.setText(text["pricing_label"])
        self.summary_group.setTitle(text["summary_group"])
        self.summary_sections["core"].setText("Results")
        self.summary_sections["tokens"].setText("Token Breakdown")
        self.summary_sections["context"].setText("Runtime Context")
        self.details_title_label.setText("Thread Details")
        if self.language == "zh":
            self.summary_sections["core"].setText("\u7ed3\u679c")
            self.summary_sections["tokens"].setText("Token \u6784\u6210")
            self.summary_sections["context"].setText("\u8fd0\u884c\u4e0a\u4e0b\u6587")
            self.details_title_label.setText("\u7ebf\u7a0b\u8be6\u60c5")

        for key, caption in self.kpi_labels.items():
            if key == "primary_remaining_percent":
                caption.setText("5 \u5c0f\u65f6\u989d\u5ea6" if self.language == "zh" else "5h Limit")
            elif key == "secondary_remaining_percent":
                caption.setText("\u5468\u989d\u5ea6" if self.language == "zh" else "Weekly Limit")
            else:
                caption.setText(text["summary_rows"].get(key, key))

        for key, caption in self.detail_caption_labels.items():
            caption.setText(text["details"].get(key, key))

        self.details_empty_label.setText(text["no_active_threads"])
        self.thread_table.setHorizontalHeaderLabels(text["thread_columns"])
        self.statusBar().showMessage(text["status_ready"])

        if self.current_report is not None:
            self.populate_summary(self.current_report)
            self.populate_threads(self.current_threads)
            self.update_details()

    def populate_threads(self, threads: list[dict]) -> None:
        text = self.current_text()
        self.thread_table.setSortingEnabled(False)
        self.thread_table.clearContents()
        self.thread_table.setRowCount(len(threads))

        for row_index, thread in enumerate(threads):
            self._set_text_item(row_index, 0, thread["title"] or text["not_found"])
            self._set_text_item(row_index, 1, thread["model"] or text["not_found"])
            self._set_text_item(row_index, 2, thread["last_activity"] or "-")
            self._set_token_item(row_index, 3, thread["input_tokens"])
            self._set_token_item(row_index, 4, thread["cached_input_tokens"])
            self._set_token_item(row_index, 5, thread["output_tokens"])
            self._set_token_item(row_index, 6, thread["reasoning_output_tokens"])
            self._set_token_item(row_index, 7, thread["total_tokens"])
            self._set_float_item(row_index, 8, thread["cache_hit_rate"])
            self._set_cost_item(row_index, 9, thread["estimated_cost_usd"], text["cost_unavailable"])
            self.thread_table.item(row_index, 0).setData(Qt.ItemDataRole.UserRole, thread)

        self.thread_table.setSortingEnabled(True)
        self.thread_table.sortItems(2, Qt.SortOrder.DescendingOrder)

        if threads:
            self.thread_table.selectRow(0)
            self.details_empty_label.hide()
            self.details_scroll.show()
        else:
            self.thread_table.clearSelection()
            self._show_details_empty(text["no_active_threads"])

    def update_details(self) -> None:
        selected_rows = self.thread_table.selectionModel().selectedRows()
        if not selected_rows:
            self._show_details_empty(self.current_text()["no_active_threads"])
            return

        row_index = selected_rows[0].row()
        item = self.thread_table.item(row_index, 0)
        if item is None:
            self._show_details_empty(self.current_text()["no_active_threads"])
            return

        thread = item.data(Qt.ItemDataRole.UserRole)
        if not thread:
            self._show_details_empty(self.current_text()["no_active_threads"])
            return

        self.details_empty_label.hide()
        self.details_scroll.show()
        not_found = self.current_text()["not_found"]

        self._set_detail_value("title", thread["title"] or not_found)
        self._set_detail_value("title_source", thread["title_source"] or "-")
        self._set_detail_value("thread_id", thread["thread_id"] or "-")
        self._set_detail_value("model", thread["model"] or not_found)
        self._set_detail_value("last_activity", thread["last_activity"] or "-")
        self._set_detail_value("latest_usage_ts", thread["latest_usage_ts"] or "-")
        self._set_detail_value("message_round_count", str(thread.get("message_round_count", 0)))
        self._set_detail_value(
            "avg_tokens_per_round",
            format_short_number(thread.get("avg_tokens_per_round", 0.0)),
            tooltip=f"{thread.get('avg_tokens_per_round', 0.0):,.2f}",
        )
        self._set_detail_value("tool_call_count", str(thread.get("tool_call_count", 0)))
        self._set_detail_value(
            "output_ratio",
            f"{thread.get('output_ratio', 0.0):.2f}%",
            tooltip=f"{thread.get('output_ratio', 0.0):.4f}%",
        )
        self._set_detail_value("input_tokens", f"{thread['input_tokens']:,}")
        self._set_detail_value("cached_input_tokens", f"{thread['cached_input_tokens']:,}")
        self._set_detail_value("output_tokens", f"{thread['output_tokens']:,}")
        self._set_detail_value("reasoning_output_tokens", f"{thread['reasoning_output_tokens']:,}")
        self._set_detail_value("total_tokens", f"{thread['total_tokens']:,}")
        self._set_detail_value("cache_hit_rate", f"{thread['cache_hit_rate']:.2f}%")
        self._set_detail_value("estimated_cost_usd", self.format_cost(thread["estimated_cost_usd"]))
        self._set_detail_value("file", thread["file"])

    def _show_details_empty(self, message: str) -> None:
        self.details_empty_label.setText(message)
        self.details_empty_label.show()
        self.details_scroll.hide()
        for value_label in self.detail_value_labels.values():
            value_label.setText("-")
            value_label.setToolTip("")

    def _set_detail_value(self, key: str, text: str, tooltip: str | None = None) -> None:
        label = self.detail_value_labels[key]
        label.setText(text)
        label.setToolTip(tooltip or text)


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
    window.showMaximized()
    return app.exec()
