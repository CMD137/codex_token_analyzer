from __future__ import annotations

import argparse
import sys

from analyzer_core import UTC, UTC_PLUS_8, load_report

LANGUAGE_CONFIG = {
    "zh": {
        "timezone": UTC_PLUS_8,
        "no_data": "未找到最近线程用量或额度信息。",
        "active_threads_header": "活跃线程",
        "window_start": "窗口开始",
        "window_end": "窗口结束",
        "active_thread_count": "活跃线程数",
        "sum_input_tokens": "输入 token 总计",
        "sum_cached_input_tokens": "缓存输入 token",
        "sum_output_tokens": "输出 token 总计",
        "sum_reasoning_output_tokens": "推理输出 token",
        "sum_total_tokens": "总 token",
        "aggregate_cache_hit_rate": "整体缓存命中率",
        "thread": "线程",
        "title": "标题",
        "title_source": "标题来源",
        "thread_id": "线程 ID",
        "file": "文件",
        "last_activity": "最近活动",
        "latest_usage_ts": "最近用量时间",
        "input_tokens": "输入 token",
        "cached_input_tokens": "缓存输入 token",
        "output_tokens": "输出 token",
        "reasoning_output_tokens": "推理输出 token",
        "total_tokens": "总 token",
        "cache_hit_rate": "缓存命中率",
        "rate_limits_header": "额度",
        "latest_limits_file": "最新额度文件",
        "limits_timestamp": "额度时间",
        "primary_used_percent": "5 小时已用",
        "primary_remaining_percent": "5 小时剩余",
        "secondary_used_percent": "周额度已用",
        "secondary_remaining_percent": "周额度剩余",
        "plan_type": "套餐",
        "no_rate_limits": "未找到额度信息。",
        "gui_dependency_missing": "缺少 GUI 依赖：PySide6",
        "install_hint": "请先执行：pip install PySide6",
        "active_threads_banner": "=== 活跃线程 (最近 {days} 天, {timezone}) ===",
        "rate_limits_banner": "=== 额度 ({timezone}) ===",
        "not_found": "(未找到)",
    },
    "en": {
        "timezone": UTC,
        "no_data": "No recent thread usage or rate limits found.",
        "active_threads_header": "ACTIVE THREADS",
        "window_start": "window start",
        "window_end": "window end",
        "active_thread_count": "active thread count",
        "sum_input_tokens": "sum input tokens",
        "sum_cached_input_tokens": "sum cached input",
        "sum_output_tokens": "sum output tokens",
        "sum_reasoning_output_tokens": "sum reasoning output",
        "sum_total_tokens": "sum total tokens",
        "aggregate_cache_hit_rate": "aggregate cache hit",
        "thread": "Thread",
        "title": "title",
        "title_source": "title source",
        "thread_id": "thread id",
        "file": "file",
        "last_activity": "last activity",
        "latest_usage_ts": "latest usage ts",
        "input_tokens": "input tokens",
        "cached_input_tokens": "cached input tokens",
        "output_tokens": "output tokens",
        "reasoning_output_tokens": "reasoning output",
        "total_tokens": "total tokens",
        "cache_hit_rate": "cache hit rate",
        "rate_limits_header": "RATE LIMITS",
        "latest_limits_file": "latest limits file",
        "limits_timestamp": "limits timestamp",
        "primary_used_percent": "5h used",
        "primary_remaining_percent": "5h remaining",
        "secondary_used_percent": "weekly used",
        "secondary_remaining_percent": "weekly remaining",
        "plan_type": "plan",
        "no_rate_limits": "No rate limits found.",
        "gui_dependency_missing": "GUI dependency missing: PySide6",
        "install_hint": "Install it with: pip install PySide6",
        "active_threads_banner": "=== ACTIVE THREADS (LAST {days} DAYS, {timezone}) ===",
        "rate_limits_banner": "=== RATE LIMITS ({timezone}) ===",
        "not_found": "(not found)",
    },
}


def get_language_config(language: str) -> dict[str, object]:
    return LANGUAGE_CONFIG[language]


def print_metric(label: str, value: str) -> None:
    print(f"{label:<22} : {value}")


def print_report(window_days: int, language: str) -> int:
    config = get_language_config(language)
    report = load_report(window_days, display_timezone=config["timezone"])
    active_threads = report["threads"]
    rate_limits = report["rate_limits"]

    if not active_threads and not rate_limits:
        print(config["no_data"])
        return 0

    summary = report["summary"]

    print(f"\n{config['active_threads_banner'].format(days=window_days, timezone=report['timezone_label'])}\n")
    print_metric(str(config["window_start"]), str(report["window_start"]))
    print_metric(str(config["window_end"]), str(report["window_end"]))
    print_metric(str(config["active_thread_count"]), str(report["active_thread_count"]))
    print()
    print_metric(str(config["sum_input_tokens"]), f"{summary['input_tokens']:,}")
    print_metric(str(config["sum_cached_input_tokens"]), f"{summary['cached_input_tokens']:,}")
    print_metric(str(config["sum_output_tokens"]), f"{summary['output_tokens']:,}")
    print_metric(str(config["sum_reasoning_output_tokens"]), f"{summary['reasoning_output_tokens']:,}")
    print_metric(str(config["sum_total_tokens"]), f"{summary['total_tokens']:,}")
    print_metric(str(config["aggregate_cache_hit_rate"]), f"{summary['aggregate_cache_hit_rate']:.2f}%")

    for index, thread in enumerate(active_threads, start=1):
        print(f"\n--- {config['thread']} {index} ---")
        print_metric(str(config["title"]), thread["title"] or str(config["not_found"]))
        print_metric(str(config["title_source"]), thread["title_source"])
        if thread["thread_id"]:
            print_metric(str(config["thread_id"]), thread["thread_id"])
        print_metric(str(config["file"]), thread["file"])
        print_metric(str(config["last_activity"]), thread["last_activity"])
        print_metric(str(config["latest_usage_ts"]), thread["latest_usage_ts"])
        print_metric(str(config["input_tokens"]), f"{thread['input_tokens']:,}")
        print_metric(str(config["cached_input_tokens"]), f"{thread['cached_input_tokens']:,}")
        print_metric(str(config["output_tokens"]), f"{thread['output_tokens']:,}")
        print_metric(str(config["reasoning_output_tokens"]), f"{thread['reasoning_output_tokens']:,}")
        print_metric(str(config["total_tokens"]), f"{thread['total_tokens']:,}")
        print_metric(str(config["cache_hit_rate"]), f"{thread['cache_hit_rate']:.2f}%")

    print(f"\n{config['rate_limits_banner'].format(timezone=report['timezone_label'])}\n")
    if rate_limits:
        print_metric(str(config["latest_limits_file"]), rate_limits["file"])
        print_metric(str(config["limits_timestamp"]), rate_limits["timestamp"])
        print()
        print_metric(str(config["primary_used_percent"]), f"{rate_limits['primary_used_percent']:.1f}%")
        print_metric(str(config["primary_remaining_percent"]), f"{rate_limits['primary_remaining_percent']:.1f}%")
        print_metric(str(config["secondary_used_percent"]), f"{rate_limits['secondary_used_percent']:.1f}%")
        print_metric(str(config["secondary_remaining_percent"]), f"{rate_limits['secondary_remaining_percent']:.1f}%")
        print_metric(str(config["plan_type"]), str(rate_limits["plan_type"]))
    else:
        print(config["no_rate_limits"])

    return 0


def launch_gui(language: str) -> int:
    config = get_language_config(language)
    try:
        from codex_token_analyzer_gui import run
    except ModuleNotFoundError as exc:
        if exc.name == "PySide6":
            print(config["gui_dependency_missing"])
            print(config["install_hint"])
            return 1
        raise

    return run(initial_language=language)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze Codex token usage from local session files.")
    parser.add_argument("--days", type=int, default=7, help="Recent window size in days. Default: 7")
    parser.add_argument("--lang", choices=("zh", "en"), default="zh", help="Display language. zh uses UTC+8, en uses UTC.")
    parser.add_argument("--gui", action="store_true", help="Launch the desktop GUI.")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.days < 1:
        parser.error("--days must be at least 1")

    if args.gui:
        return launch_gui(args.lang)

    return print_report(args.days, args.lang)


if __name__ == "__main__":
    sys.exit(main())
