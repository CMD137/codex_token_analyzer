import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

SESSIONS_BASE = Path.home() / ".codex" / "sessions"
SESSION_INDEX = Path.home() / ".codex" / "session_index.jsonl"
STATE_DB = Path.home() / ".codex" / "state_5.sqlite"
WINDOW_DAYS = 7

WINDOW_END = datetime.now(timezone.utc)
WINDOW_START = WINDOW_END - timedelta(days=WINDOW_DAYS)


def parse_timestamp(value):
    if not value:
        return None

    try:
        if value.endswith("Z"):
            value = value[:-1] + "+00:00"
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def iso_z(dt):
    return dt.isoformat().replace("+00:00", "Z")


def read_session_index_titles():
    titles = {}

    if not SESSION_INDEX.exists():
        return titles

    with open(SESSION_INDEX, encoding="utf-8", errors="ignore") as f:
        for line in f:
            try:
                data = json.loads(line)
            except Exception:
                continue

            thread_id = data.get("id")
            thread_name = (data.get("thread_name") or "").strip()
            updated_at = data.get("updated_at")

            if thread_id and thread_name:
                titles[thread_id] = {
                    "title": thread_name,
                    "updated_at": updated_at,
                }

    return titles


def read_state_titles():
    titles = {}

    if not STATE_DB.exists():
        return titles

    conn = sqlite3.connect(STATE_DB)
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, title, updated_at_ms FROM threads")
        for thread_id, title, updated_at_ms in cur.fetchall():
            title = (title or "").strip()
            if thread_id and title:
                titles[thread_id] = {
                    "title": title,
                    "updated_at_ms": updated_at_ms,
                }
    finally:
        conn.close()

    return titles


session_index_titles = read_session_index_titles()
state_titles = read_state_titles()
threads = {}
latest_limits = None

for file in SESSIONS_BASE.glob("**/*.jsonl"):
    file_key = str(file)
    thread = threads.setdefault(
        file_key,
        {
            "file": file_key,
            "thread_id": None,
            "title": None,
            "title_source": None,
            "last_activity": None,
            "last_activity_text": None,
            "latest_usage": None,
            "latest_usage_ts": None,
            "latest_usage_text": None,
            "context_window": None,
            "cwd": None,
        },
    )

    with open(file, encoding="utf-8", errors="ignore") as f:
        for line in f:
            try:
                data = json.loads(line)
            except Exception:
                continue

            payload = data.get("payload") or {}
            ts_text = data.get("timestamp", "")
            ts = parse_timestamp(ts_text)

            if ts and (thread["last_activity"] is None or ts > thread["last_activity"]):
                thread["last_activity"] = ts
                thread["last_activity_text"] = ts_text

            if data.get("type") == "session_meta":
                session_id = payload.get("id")
                if session_id:
                    thread["thread_id"] = session_id

                if payload.get("cwd"):
                    thread["cwd"] = payload.get("cwd")

            info = payload.get("info") or {}
            usage = info.get("total_token_usage")
            if usage and ts and (thread["latest_usage_ts"] is None or ts > thread["latest_usage_ts"]):
                thread["latest_usage"] = usage
                thread["latest_usage_ts"] = ts
                thread["latest_usage_text"] = ts_text
                thread["context_window"] = info.get("model_context_window")

            rate_limits = payload.get("rate_limits") or {}
            if rate_limits and ts:
                if latest_limits is None or ts > latest_limits["timestamp"]:
                    latest_limits = {
                        "timestamp": ts,
                        "timestamp_text": ts_text,
                        "file": file_key,
                        "rate_limits": rate_limits,
                    }

for thread in threads.values():
    thread_id = thread.get("thread_id")
    if thread_id and thread_id in session_index_titles:
        thread["title"] = session_index_titles[thread_id]["title"]
        thread["title_source"] = "session_index.jsonl"
    elif thread_id and thread_id in state_titles:
        thread["title"] = state_titles[thread_id]["title"]
        thread["title_source"] = "state_5.sqlite"
    else:
        thread["title"] = None
        thread["title_source"] = "not_found"

active_threads = []
for thread in threads.values():
    if thread["last_activity"] is None:
        continue
    if thread["last_activity"] < WINDOW_START:
        continue
    if not thread["latest_usage"]:
        continue
    active_threads.append(thread)

active_threads.sort(key=lambda item: item["last_activity"], reverse=True)

if not active_threads and not latest_limits:
    print("No recent thread usage or rate limits found.")
    raise SystemExit

sum_input = sum(t["latest_usage"].get("input_tokens", 0) for t in active_threads)
sum_cached = sum(t["latest_usage"].get("cached_input_tokens", 0) for t in active_threads)
sum_output = sum(t["latest_usage"].get("output_tokens", 0) for t in active_threads)
sum_reasoning = sum(t["latest_usage"].get("reasoning_output_tokens", 0) for t in active_threads)
sum_total = sum(t["latest_usage"].get("total_tokens", 0) for t in active_threads)
aggregate_cache_hit = (sum_cached / sum_input * 100) if sum_input else 0.0

print("\n=== ACTIVE THREADS (LAST 7 DAYS) ===\n")
print(f"window start          : {iso_z(WINDOW_START)}")
print(f"window end            : {iso_z(WINDOW_END)}")
print(f"active thread count   : {len(active_threads)}")
print()
print(f"sum input tokens      : {sum_input:,}")
print(f"sum cached input      : {sum_cached:,}")
print(f"sum output tokens     : {sum_output:,}")
print(f"sum reasoning output  : {sum_reasoning:,}")
print(f"sum total tokens      : {sum_total:,}")
print(f"aggregate cache hit   : {aggregate_cache_hit:.2f}%")

for index, thread in enumerate(active_threads, start=1):
    usage = thread["latest_usage"]
    input_tokens = usage.get("input_tokens", 0)
    cached_tokens = usage.get("cached_input_tokens", 0)
    cache_hit = (cached_tokens / input_tokens * 100) if input_tokens else 0.0

    print(f"\n--- Thread {index} ---")
    print(f"title                 : {thread['title'] or '(not found)'}")
    print(f"title source          : {thread['title_source']}")
    if thread.get("thread_id"):
        print(f"thread id             : {thread['thread_id']}")
    print(f"file                  : {thread['file']}")
    if thread.get("cwd"):
        print(f"cwd                   : {thread['cwd']}")
    print(f"last activity         : {thread['last_activity_text']}")
    print(f"latest usage ts       : {thread['latest_usage_text']}")
    print(f"input tokens          : {input_tokens:,}")
    print(f"cached input tokens   : {cached_tokens:,}")
    print(f"output tokens         : {usage.get('output_tokens', 0):,}")
    print(f"reasoning output      : {usage.get('reasoning_output_tokens', 0):,}")
    print(f"total tokens          : {usage.get('total_tokens', 0):,}")
    print(f"cache hit rate        : {cache_hit:.2f}%")

    context_window = thread.get("context_window")
    if context_window:
        print(f"context win           : {context_window:,}")

print("\n=== RATE LIMITS ===\n")

if latest_limits:
    rl = latest_limits["rate_limits"]
    primary = rl.get("primary") or {}
    secondary = rl.get("secondary") or {}

    p_used = float(primary.get("used_percent", 0) or 0)
    s_used = float(secondary.get("used_percent", 0) or 0)

    print(f"latest limits file    : {latest_limits['file']}")
    print(f"limits timestamp      : {latest_limits['timestamp_text']}")
    print()
    print(f"5h used               : {p_used:.1f}%")
    print(f"5h remaining          : {100 - p_used:.1f}%")
    print(f"weekly used           : {s_used:.1f}%")
    print(f"weekly remaining      : {100 - s_used:.1f}%")
    print(f"plan                  : {rl.get('plan_type', 'unknown')}")
else:
    print("No rate limits found.")
