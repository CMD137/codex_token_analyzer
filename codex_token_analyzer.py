from __future__ import annotations

import argparse
import sys

from analyzer_core import load_report


def print_report(window_days: int) -> int:
    report = load_report(window_days)
    active_threads = report["threads"]
    rate_limits = report["rate_limits"]

    if not active_threads and not rate_limits:
        print("No recent thread usage or rate limits found.")
        return 0

    summary = report["summary"]

    print(f"\n=== ACTIVE THREADS (LAST {window_days} DAYS) ===\n")
    print(f"window start          : {report['window_start']}")
    print(f"window end            : {report['window_end']}")
    print(f"active thread count   : {report['active_thread_count']}")
    print()
    print(f"sum input tokens      : {summary['input_tokens']:,}")
    print(f"sum cached input      : {summary['cached_input_tokens']:,}")
    print(f"sum output tokens     : {summary['output_tokens']:,}")
    print(f"sum reasoning output  : {summary['reasoning_output_tokens']:,}")
    print(f"sum total tokens      : {summary['total_tokens']:,}")
    print(f"aggregate cache hit   : {summary['aggregate_cache_hit_rate']:.2f}%")

    for index, thread in enumerate(active_threads, start=1):
        print(f"\n--- Thread {index} ---")
        print(f"title                 : {thread['title'] or '(not found)'}")
        print(f"title source          : {thread['title_source']}")
        if thread["thread_id"]:
            print(f"thread id             : {thread['thread_id']}")
        print(f"file                  : {thread['file']}")
        print(f"last activity         : {thread['last_activity']}")
        print(f"latest usage ts       : {thread['latest_usage_ts']}")
        print(f"input tokens          : {thread['input_tokens']:,}")
        print(f"cached input tokens   : {thread['cached_input_tokens']:,}")
        print(f"output tokens         : {thread['output_tokens']:,}")
        print(f"reasoning output      : {thread['reasoning_output_tokens']:,}")
        print(f"total tokens          : {thread['total_tokens']:,}")
        print(f"cache hit rate        : {thread['cache_hit_rate']:.2f}%")

    print("\n=== RATE LIMITS ===\n")
    if rate_limits:
        print(f"latest limits file    : {rate_limits['file']}")
        print(f"limits timestamp      : {rate_limits['timestamp']}")
        print()
        print(f"5h used               : {rate_limits['primary_used_percent']:.1f}%")
        print(f"5h remaining          : {rate_limits['primary_remaining_percent']:.1f}%")
        print(f"weekly used           : {rate_limits['secondary_used_percent']:.1f}%")
        print(f"weekly remaining      : {rate_limits['secondary_remaining_percent']:.1f}%")
        print(f"plan                  : {rate_limits['plan_type']}")
    else:
        print("No rate limits found.")

    return 0


def launch_gui() -> int:
    try:
        from codex_token_analyzer_gui import run
    except ModuleNotFoundError as exc:
        if exc.name == "PySide6":
            print("GUI dependency missing: PySide6")
            print("Install it with: pip install PySide6")
            return 1
        raise

    return run()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze Codex token usage from local session files.")
    parser.add_argument("--days", type=int, default=7, help="Recent window size in days. Default: 7")
    parser.add_argument("--gui", action="store_true", help="Launch the desktop GUI.")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.days < 1:
        parser.error("--days must be at least 1")

    if args.gui:
        return launch_gui()

    return print_report(args.days)


if __name__ == "__main__":
    sys.exit(main())
