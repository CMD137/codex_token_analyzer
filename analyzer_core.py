from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from pricing import estimate_cost, get_default_profile, get_profile_names, load_pricing_config

SESSIONS_BASE = Path.home() / ".codex" / "sessions"
SESSION_INDEX = Path.home() / ".codex" / "session_index.jsonl"
STATE_DB = Path.home() / ".codex" / "state_5.sqlite"
LOGS_DB = Path.home() / ".codex" / "logs_2.sqlite"
UTC = timezone.utc
UTC_PLUS_8 = timezone(timedelta(hours=8))


def parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None

    try:
        if value.endswith("Z"):
            value = value[:-1] + "+00:00"
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def iso_z(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def timezone_label(display_timezone: timezone) -> str:
    if display_timezone == UTC:
        return "UTC"
    if display_timezone == UTC_PLUS_8:
        return "UTC+8"

    offset = display_timezone.utcoffset(None) or timedelta()
    total_minutes = int(offset.total_seconds() // 60)
    sign = "+" if total_minutes >= 0 else "-"
    total_minutes = abs(total_minutes)
    hours, minutes = divmod(total_minutes, 60)
    if minutes:
        return f"UTC{sign}{hours:02d}:{minutes:02d}"
    return f"UTC{sign}{hours}"


def format_timestamp(dt: datetime | None, display_timezone: timezone) -> str | None:
    if dt is None:
        return None

    local_dt = dt.astimezone(display_timezone).replace(microsecond=0)
    return f"{local_dt:%Y-%m-%d %H:%M:%S} {timezone_label(display_timezone)}"


def _safe_int(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def _safe_float(value: Any) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def read_session_index_titles() -> dict[str, dict[str, Any]]:
    titles: dict[str, dict[str, Any]] = {}

    if not SESSION_INDEX.exists():
        return titles

    with open(SESSION_INDEX, encoding="utf-8", errors="ignore") as file_obj:
        for line in file_obj:
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


def read_state_titles() -> dict[str, dict[str, Any]]:
    titles: dict[str, dict[str, Any]] = {}

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


def read_rate_limits_from_logs() -> dict[str, Any] | None:
    """Read the latest codex.rate_limits WebSocket event from logs_2.sqlite.

    The Codex server pushes rate limits via WebSocket; the client writes each
    event to the local log database.  This function extracts the most recent
    event and returns it in a normalised structure compatible with what
    ``load_report`` expects.
    """
    if not LOGS_DB.exists():
        return None

    conn = sqlite3.connect(f"file:///{LOGS_DB.as_posix()}?immutable=1", uri=True)
    try:
        cur = conn.cursor()
        cur.execute(
            """SELECT ts, feedback_log_body FROM logs
               WHERE feedback_log_body LIKE '%"type":"codex.rate_limits"%'
               ORDER BY ts DESC LIMIT 1"""
        )
        row = cur.fetchone()
        if not row:
            return None

        ts, body = row
        # The body is:  span_context{attrs} : more_spans : {json_payload}
        # Find the JSON object by locating the last ": {" boundary.
        idx = body.rfind(": {")
        if idx == -1:
            return None

        json_str = body[idx + 2:]
        data = json.loads(json_str)
        rl = data.get("rate_limits") or {}
        primary = rl.get("primary") or {}
        secondary = rl.get("secondary") or {}

        # Normalise into the same shape as the session-JSONL path so callers
        # can consume the report uniformly.
        return {
            "source": "logs_2.sqlite",
            "timestamp": datetime.fromtimestamp(ts, tz=timezone.utc),
            "plan_type": data.get("plan_type", "unknown"),
            "primary_used_percent": _safe_float(primary.get("used_percent")),
            "primary_remaining_percent": max(0.0, 100.0 - _safe_float(primary.get("used_percent"))),
            "primary_reset_at": _safe_float(primary.get("reset_at")),
            "secondary_used_percent": _safe_float(secondary.get("used_percent")),
            "secondary_remaining_percent": max(0.0, 100.0 - _safe_float(secondary.get("used_percent"))),
            "secondary_reset_at": _safe_float(secondary.get("reset_at")),
            "allowed": rl.get("allowed"),
            "limit_reached": rl.get("limit_reached"),
        }
    except Exception:
        return None
    finally:
        conn.close()


def load_report(
    window_days: int = 7,
    display_timezone: timezone = UTC,
    pricing_config_path: str | Path | None = None,
    pricing_profile: str | None = None,
    regional_pricing: bool = False,
) -> dict[str, Any]:
    if window_days < 1:
        raise ValueError("window_days must be at least 1")

    window_end = datetime.now(timezone.utc)
    window_start = window_end - timedelta(days=window_days)
    pricing_config = load_pricing_config(pricing_config_path)
    pricing_profile = pricing_profile or get_default_profile(pricing_config)

    session_index_titles = read_session_index_titles()
    state_titles = read_state_titles()
    threads: dict[str, dict[str, Any]] = {}
    latest_limits: dict[str, Any] | None = None

    for file_path in SESSIONS_BASE.glob("**/*.jsonl"):
        file_key = str(file_path)
        thread = threads.setdefault(
            file_key,
            {
                "file": file_key,
                "thread_id": None,
                "title": None,
                "title_source": None,
                "last_activity": None,
                "last_activity_text": None,
                "model": None,
                "latest_usage": None,
                "latest_usage_ts": None,
                "latest_usage_text": None,
                "turn_count": 0,
                "user_message_count": 0,
                "assistant_message_count": 0,
                "tool_call_count": 0,
            },
        )

        with open(file_path, encoding="utf-8", errors="ignore") as file_obj:
            for line in file_obj:
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
                    model = payload.get("model")
                    if model:
                        thread["model"] = model

                if data.get("type") == "turn_context":
                    thread["turn_count"] += 1
                    model = payload.get("model")
                    if model:
                        thread["model"] = model

                if data.get("type") == "response_item":
                    payload_type = payload.get("type")
                    if payload_type == "message":
                        role = payload.get("role")
                        if role == "user":
                            thread["user_message_count"] += 1
                        elif role == "assistant":
                            thread["assistant_message_count"] += 1
                    elif payload_type in {"function_call", "custom_tool_call"}:
                        thread["tool_call_count"] += 1

                info = payload.get("info") or {}
                usage = info.get("total_token_usage")
                if usage and ts and (thread["latest_usage_ts"] is None or ts > thread["latest_usage_ts"]):
                    thread["latest_usage"] = {
                        "input_tokens": _safe_int(usage.get("input_tokens")),
                        "cached_input_tokens": _safe_int(usage.get("cached_input_tokens")),
                        "output_tokens": _safe_int(usage.get("output_tokens")),
                        "reasoning_output_tokens": _safe_int(usage.get("reasoning_output_tokens")),
                        "total_tokens": _safe_int(usage.get("total_tokens")),
                    }
                    thread["latest_usage_ts"] = ts
                    thread["latest_usage_text"] = ts_text

                rate_limits = payload.get("rate_limits") or {}
                if rate_limits and ts:
                    if latest_limits is None or ts > latest_limits["timestamp"]:
                        primary = rate_limits.get("primary") or {}
                        secondary = rate_limits.get("secondary") or {}
                        latest_limits = {
                            "source": file_key,
                            "timestamp": ts,
                            "plan_type": rate_limits.get("plan_type", "unknown"),
                            "primary_used_percent": _safe_float(primary.get("used_percent")),
                            "primary_remaining_percent": max(0.0, 100.0 - _safe_float(primary.get("used_percent"))),
                            "primary_reset_at": _safe_float(primary.get("resets_at")),
                            "secondary_used_percent": _safe_float(secondary.get("used_percent")),
                            "secondary_remaining_percent": max(0.0, 100.0 - _safe_float(secondary.get("used_percent"))),
                            "secondary_reset_at": _safe_float(secondary.get("resets_at")),
                        }

    # Merge rate limits from both sources, preferring whichever has the most
    # recent timestamp.  logs_2.sqlite carries richer data (reset_at etc.),
    # but session-JSONL may hold the freshest usage percentages from the
    # latest turn because WebSocket pushes can lag.
    logs_limits = read_rate_limits_from_logs()
    if logs_limits:
        if latest_limits is None or logs_limits["timestamp"] > latest_limits["timestamp"]:
            latest_limits = logs_limits

    for thread in threads.values():
        thread_id = thread.get("thread_id")
        if thread_id and thread_id in session_index_titles:
            thread["title"] = session_index_titles[thread_id]["title"]
            thread["title_source"] = "session_index.jsonl"
        elif thread_id and thread_id in state_titles:
            thread["title"] = state_titles[thread_id]["title"]
            thread["title_source"] = "state_5.sqlite"
        else:
            thread["title_source"] = "not_found"

    active_threads: list[dict[str, Any]] = []
    for thread in threads.values():
        if thread["last_activity"] is None:
            continue
        if thread["last_activity"] < window_start:
            continue
        if not thread["latest_usage"]:
            continue

        usage = thread["latest_usage"]
        input_tokens = usage.get("input_tokens", 0)
        cached_tokens = usage.get("cached_input_tokens", 0)
        cache_hit_rate = (cached_tokens / input_tokens * 100) if input_tokens else 0.0
        pricing = estimate_cost(
            model=thread.get("model"),
            input_tokens=input_tokens,
            cached_input_tokens=cached_tokens,
            output_tokens=usage.get("output_tokens", 0),
            config=pricing_config,
            profile_name=pricing_profile,
            regional=regional_pricing,
        )

        active_threads.append(
            {
                "message_round_count": thread["turn_count"],
                "user_message_count": thread["user_message_count"],
                "assistant_message_count": thread["assistant_message_count"],
                "tool_call_count": thread["tool_call_count"],
                "avg_tokens_per_round": (usage.get("total_tokens", 0) / thread["turn_count"]) if thread["turn_count"] else 0.0,
                "output_ratio": (usage.get("output_tokens", 0) / usage.get("total_tokens", 0) * 100)
                if usage.get("total_tokens", 0)
                else 0.0,
                "title": thread["title"],
                "title_source": thread["title_source"],
                "thread_id": thread["thread_id"],
                "file": thread["file"],
                "model": thread.get("model"),
                "last_activity": format_timestamp(thread["last_activity"], display_timezone),
                "last_activity_sort": iso_z(thread["last_activity"]),
                "latest_usage_ts": format_timestamp(thread["latest_usage_ts"], display_timezone),
                "input_tokens": input_tokens,
                "cached_input_tokens": cached_tokens,
                "output_tokens": usage.get("output_tokens", 0),
                "reasoning_output_tokens": usage.get("reasoning_output_tokens", 0),
                "total_tokens": usage.get("total_tokens", 0),
                "cache_hit_rate": cache_hit_rate,
                "pricing_status": pricing["status"],
                "pricing_model": pricing.get("resolved_model"),
                "estimated_cost_usd": pricing.get("estimated_cost_usd"),
                "pricing_profile": pricing_profile,
                "regional_pricing": regional_pricing,
                "regional_uplift_percent": pricing.get("regional_uplift_percent", 0.0),
            }
        )

    active_threads.sort(key=lambda item: item["last_activity_sort"], reverse=True)

    summary = {
        "input_tokens": sum(t["input_tokens"] for t in active_threads),
        "cached_input_tokens": sum(t["cached_input_tokens"] for t in active_threads),
        "output_tokens": sum(t["output_tokens"] for t in active_threads),
        "reasoning_output_tokens": sum(t["reasoning_output_tokens"] for t in active_threads),
        "total_tokens": sum(t["total_tokens"] for t in active_threads),
        "estimated_cost_usd": sum((t["estimated_cost_usd"] or 0.0) for t in active_threads),
        "priced_thread_count": sum(1 for t in active_threads if t["estimated_cost_usd"] is not None),
        "unpriced_thread_count": sum(1 for t in active_threads if t["estimated_cost_usd"] is None),
    }
    summary["aggregate_cache_hit_rate"] = (
        summary["cached_input_tokens"] / summary["input_tokens"] * 100 if summary["input_tokens"] else 0.0
    )

    rate_limits_report = None
    if latest_limits:

        def _format_reset_at(ts_float: float | None) -> str | None:
            if not ts_float or ts_float <= 0:
                return None
            dt = datetime.fromtimestamp(ts_float, tz=timezone.utc)
            return format_timestamp(dt, display_timezone)

        rate_limits_report = {
            "source": latest_limits.get("source", ""),
            "timestamp": format_timestamp(latest_limits["timestamp"], display_timezone),
            "plan_type": latest_limits.get("plan_type", "unknown"),
            "primary_used_percent": latest_limits["primary_used_percent"],
            "primary_remaining_percent": latest_limits["primary_remaining_percent"],
            "primary_reset_at": _format_reset_at(latest_limits.get("primary_reset_at")),
            "secondary_used_percent": latest_limits["secondary_used_percent"],
            "secondary_remaining_percent": latest_limits["secondary_remaining_percent"],
            "secondary_reset_at": _format_reset_at(latest_limits.get("secondary_reset_at")),
        }

    return {
        "window_days": window_days,
        "window_start": format_timestamp(window_start, display_timezone),
        "window_end": format_timestamp(window_end, display_timezone),
        "active_thread_count": len(active_threads),
        "summary": summary,
        "threads": active_threads,
        "rate_limits": rate_limits_report,
        "timezone_label": timezone_label(display_timezone),
        "pricing_profile": pricing_profile,
        "pricing_config_path": pricing_config["_resolved_path"],
        "pricing_profiles": get_profile_names(pricing_config),
        "regional_pricing": regional_pricing,
    }
