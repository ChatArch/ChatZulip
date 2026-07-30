"""Importable Zulip operations behind the CLI and MCP adapters."""

from __future__ import annotations

import datetime as dt
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, Union

from .client import JsonDict, ZulipClient
from .config import ZulipConfig


def parse_csv(value: Optional[str]) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def build_narrow(
    *,
    stream: str | None = None,
    topic: str | None = None,
    sender: str | None = None,
    search: str | None = None,
) -> list[JsonDict] | None:
    narrow: list[JsonDict] = []
    if stream:
        narrow.append({"operator": "stream", "operand": stream})
    if topic:
        narrow.append({"operator": "topic", "operand": topic})
    if sender:
        narrow.append({"operator": "sender", "operand": sender})
    if search:
        narrow.append({"operator": "search", "operand": search})
    return narrow or None


def coerce_int(value: Optional[int], fallback: object, label: str) -> int:
    if value is not None:
        return int(value)
    try:
        return int(str(fallback))
    except Exception as exc:
        raise ValueError(f"Invalid {label} value: {fallback}") from exc


def clean_text(text: str, max_len: int = 200) -> str:
    cleaned = " ".join((text or "").split())
    if len(cleaned) > max_len:
        return cleaned[: max_len - 3] + "..."
    return cleaned


def format_ts(timestamp: int) -> str:
    return dt.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")


def resolve_stream_id(client: Any, stream: str) -> int | None:
    if stream.isdigit():
        return int(stream)

    for item in client.list_subscriptions():
        if item.get("name") == stream:
            return item.get("stream_id")

    for item in client.list_streams(include_public=True):
        if item.get("name") == stream:
            return item.get("stream_id")
    return None


def render_messages(messages: list[JsonDict]) -> str:
    lines: list[str] = []
    for message in messages:
        timestamp = format_ts(message.get("timestamp", 0))
        sender = message.get("sender_full_name") or message.get("sender_email") or "unknown"
        stream = message.get("display_recipient") or message.get("stream") or ""
        topic = message.get("subject") or ""
        prefix = f"[{timestamp}] {sender}"
        if stream or topic:
            prefix += f" ({stream}/{topic})"
        lines.append(f"{prefix}: {clean_text(message.get('content', ''), 300)}")
    return "\n".join(lines)


def render_topic_markdown(stream: str, topic: str, messages: list[JsonDict]) -> str:
    lines = [f"# {stream} / {topic}", ""]
    for message in messages:
        timestamp = format_ts(message.get("timestamp", 0))
        sender = message.get("sender_full_name") or message.get("sender_email") or "unknown"
        content = message.get("content") or ""
        lines.extend([f"## {timestamp} - {sender}", "", content, ""])
    return "\n".join(lines).rstrip() + "\n"


def ensure_client(client: Any | None = None) -> Any:
    return client if client is not None else ZulipClient()


def list_streams(client: Any | None = None, *, include_public: bool = False) -> list[JsonDict]:
    client = ensure_client(client)
    return client.list_streams(include_public=True) if include_public else client.list_subscriptions()


def list_topics(stream: str, client: Any | None = None) -> list[JsonDict]:
    client = ensure_client(client)
    stream_id = resolve_stream_id(client, stream)
    if stream_id is None:
        raise ValueError(f"Stream not found: {stream}")
    return client.list_topics(stream_id)


def get_messages(
    *,
    anchor: Union[int, str] = "newest",
    num_before: int = 20,
    num_after: int = 0,
    stream: str | None = None,
    topic: str | None = None,
    sender: str | None = None,
    search: str | None = None,
    client: Any | None = None,
) -> list[JsonDict]:
    client = ensure_client(client)
    return client.get_messages(
        anchor=anchor,
        num_before=num_before,
        num_after=num_after,
        narrow=build_narrow(stream=stream, topic=topic, sender=sender, search=search),
    )


def get_topic_messages(
    stream: Union[int, str],
    topic: str,
    *,
    batch_size: int = 200,
    max_requests: int = 200,
    client: Any | None = None,
) -> list[JsonDict]:
    client = ensure_client(client)
    return client.get_topic_messages(stream, topic, batch_size=batch_size, max_requests=max_requests)


def send_message(
    *,
    to: Union[str, list[int], list[str]],
    content: str,
    type: str = "stream",
    topic: Optional[str] = None,
    client: Any | None = None,
) -> int | None:
    client = ensure_client(client)
    result = client.send_message(type=type, to=to, content=content, topic=topic)
    return result.get("id")


def react(
    *,
    message_id: int,
    emoji_name: str,
    reaction_type: str = "unicode",
    client: Any | None = None,
) -> bool:
    client = ensure_client(client)
    result = client.react_to_message(message_id, emoji_name, reaction_type=reaction_type)
    return result.get("result") == "success"


def upload_file(file_path: str, client: Any | None = None) -> str:
    client = ensure_client(client)
    return client.upload_file(file_path)


def render_fallback_summary(messages: list[JsonDict]) -> str:
    topic_counter: dict[str, int] = {}
    for message in messages:
        stream = message.get("display_recipient") or message.get("stream") or "unknown"
        topic = message.get("subject") or "unknown"
        key = f"{stream} / {topic}"
        topic_counter[key] = topic_counter.get(key, 0) + 1

    lines = ["- Rule-based summary: LLM summary unavailable."]
    for name, count in sorted(topic_counter.items(), key=lambda item: item[1], reverse=True)[:5]:
        lines.append(f"- {name}: {count} messages")
    return "\n".join(lines)


def llm_summarize(
    messages: list[JsonDict],
    streams: list[str],
    topics: list[str],
    since_hours: int,
    model: Optional[str],
    max_tokens: int,
    temperature: float,
) -> str:
    try:
        from chattool.llm import Chat  # type: ignore[import-not-found]
    except Exception as exc:
        raise RuntimeError("optional chattool LLM summarizer is unavailable") from exc

    sample = messages[-min(len(messages), 200) :]
    lines = []
    for message in sample:
        timestamp = format_ts(message.get("timestamp", 0))
        stream_name = message.get("display_recipient") or message.get("stream") or "unknown"
        topic_name = message.get("subject") or "unknown"
        sender_name = message.get("sender_full_name") or "unknown"
        content = clean_text(message.get("content", ""), max_len=240)
        lines.append(f"- [{timestamp}] {stream_name} / {topic_name} | {sender_name}: {content}")

    chat = Chat(
        messages=[
            {
                "role": "system",
                "content": "Summarize Zulip messages concisely. Do not invent details.",
            },
            {
                "role": "user",
                "content": "\n".join(
                    [
                        f"Time window: last {since_hours} hours",
                        f"Streams: {', '.join(streams) if streams else 'ALL'}",
                        f"Topics: {', '.join(topics) if topics else 'ALL'}",
                        "",
                        "Messages (chronological):",
                        *lines,
                    ]
                ),
            },
        ]
    )
    response = chat.get_response(max_tokens=max_tokens, temperature=temperature, model=model)
    return (response.content or "").strip()


def render_news_markdown(
    *,
    messages: list[JsonDict],
    summary: str,
    streams: list[str],
    topics: list[str],
    since_hours: int,
    since_ts: int,
    output_time: dt.datetime,
) -> str:
    lines = [
        f"# Zulip News ({output_time.strftime('%Y-%m-%d %H:%M')})",
        "",
        f"- Window: last {since_hours} hours ({format_ts(since_ts)} ~ {output_time.strftime('%Y-%m-%d %H:%M:%S')})",
        f"- Streams: {', '.join(streams) if streams else 'ALL'}",
        f"- Topics: {', '.join(topics) if topics else 'ALL'}",
        f"- Messages: {len(messages)}",
        "",
        "## Summary",
        summary.strip() if summary else "(no summary)",
        "",
        "## Hot Topics",
    ]

    topic_counter: dict[str, int] = {}
    for message in messages:
        stream_name = message.get("display_recipient") or message.get("stream") or "unknown"
        topic_name = message.get("subject") or "unknown"
        key = f"{stream_name} / {topic_name}"
        topic_counter[key] = topic_counter.get(key, 0) + 1
    top_topics = sorted(topic_counter.items(), key=lambda item: item[1], reverse=True)[:10]
    lines.extend([f"- {name} ({count})" for name, count in top_topics] or ["- (none)"])
    lines.extend(["", "## Selected Messages"])
    if not messages:
        lines.append("- (none)")
        return "\n".join(lines)

    for message in messages[: min(30, len(messages))]:
        timestamp = format_ts(message.get("timestamp", 0))
        stream_name = message.get("display_recipient") or message.get("stream") or "unknown"
        topic_name = message.get("subject") or "unknown"
        sender_name = message.get("sender_full_name") or "unknown"
        content = clean_text(message.get("content", ""), max_len=180)
        lines.append(f"- [{timestamp}] **{stream_name}** / *{topic_name}* - {sender_name}: {content}")
    return "\n".join(lines)


@dataclass
class NewsResult:
    messages: list[JsonDict]
    markdown: str
    output_path: Path
    used_fallback: bool
    fallback_reason: str | None = None


def summarize_news(
    *,
    streams: list[str] | None = None,
    topics: list[str] | None = None,
    since_hours: int | None = None,
    per_stream: int | None = None,
    limit: int | None = None,
    output: str | None = None,
    model: str | None = None,
    max_tokens: int = 800,
    temperature: float = 0.2,
    client: Any | None = None,
) -> NewsResult:
    client = ensure_client(client)
    cfg_streams = parse_csv(ZulipConfig.ZULIP_NEWS_STREAMS.value)
    cfg_topics = parse_csv(ZulipConfig.ZULIP_NEWS_TOPICS.value)
    selected_streams = list(streams or []) or cfg_streams
    selected_topics = list(topics or []) or cfg_topics
    selected_since_hours = coerce_int(
        since_hours, ZulipConfig.ZULIP_NEWS_SINCE_HOURS.value or 24, "since-hours"
    )
    selected_per_stream = coerce_int(
        per_stream, ZulipConfig.ZULIP_NEWS_PER_STREAM.value or 200, "per-stream"
    )

    if not selected_streams:
        selected_streams = [
            str(item.get("name")) for item in client.list_subscriptions() if item.get("name")
        ]
    if not selected_streams:
        selected_streams = [
            str(item.get("name"))
            for item in client.list_streams(include_public=False)
            if item.get("name")
        ]
    if not selected_streams:
        raise ValueError("No streams available. Set ZULIP_NEWS_STREAMS or pass --stream.")

    now = int(time.time())
    since_ts = now - selected_since_hours * 3600
    all_messages: list[JsonDict] = []
    for stream in selected_streams:
        messages = client.get_messages(
            anchor="newest",
            num_before=selected_per_stream,
            num_after=0,
            narrow=[{"operator": "stream", "operand": stream}],
        )
        for message in messages:
            if message.get("timestamp", 0) < since_ts:
                continue
            if selected_topics and message.get("subject") not in selected_topics:
                continue
            all_messages.append(message)

    all_messages.sort(key=lambda item: item.get("timestamp", 0))
    if limit:
        all_messages = all_messages[-limit:]

    used_fallback = False
    fallback_reason = None
    if not all_messages:
        summary = "No messages matched the criteria."
    else:
        try:
            summary = llm_summarize(
                all_messages,
                selected_streams,
                selected_topics,
                selected_since_hours,
                model,
                max_tokens,
                temperature,
            )
        except Exception as exc:
            used_fallback = True
            fallback_reason = str(exc)
            summary = render_fallback_summary(all_messages)

    output_time = dt.datetime.now()
    selected_messages = list(reversed(all_messages)) if len(all_messages) > 30 else all_messages
    markdown = render_news_markdown(
        messages=selected_messages,
        summary=summary,
        streams=selected_streams,
        topics=selected_topics,
        since_hours=selected_since_hours,
        since_ts=since_ts,
        output_time=output_time,
    )
    output_path = Path(output or f"zulip-news-{output_time.strftime('%Y%m%d')}.md")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown, encoding="utf-8")
    return NewsResult(
        messages=all_messages,
        markdown=markdown,
        output_path=output_path,
        used_fallback=used_fallback,
        fallback_reason=fallback_reason,
    )


__all__ = [
    "NewsResult",
    "build_narrow",
    "get_messages",
    "get_topic_messages",
    "list_streams",
    "list_topics",
    "react",
    "render_messages",
    "render_topic_markdown",
    "send_message",
    "summarize_news",
    "upload_file",
]
