"""MCP adapters for Zulip operations."""

from __future__ import annotations

from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from fastmcp import FastMCP
else:  # pragma: no cover - optional runtime dependency
    FastMCP = Any

from . import operations


def list_streams(include_public: bool = True) -> list[dict[str, Any]]:
    """List subscribed or accessible public Zulip streams."""

    return operations.list_streams(include_public=include_public)


def list_topics(stream_id: int) -> list[dict[str, Any]]:
    """List topics for a stream by stream ID."""

    client = operations.ZulipClient()
    return client.list_topics(stream_id)


def get_messages(
    anchor: Union[int, str] = "newest",
    num_before: int = 20,
    num_after: int = 0,
    stream: Optional[str] = None,
    topic: Optional[str] = None,
    sender: Optional[str] = None,
    search: Optional[str] = None,
) -> list[dict[str, Any]]:
    """Get messages from Zulip with optional narrow filters."""

    return operations.get_messages(
        anchor=anchor,
        num_before=num_before,
        num_after=num_after,
        stream=stream,
        topic=topic,
        sender=sender,
        search=search,
    )


def get_topic_messages(
    stream: Union[int, str],
    topic: str,
    batch_size: int = 200,
    max_requests: int = 200,
) -> list[dict[str, Any]]:
    """Get full topic message history."""

    return operations.get_topic_messages(
        stream=stream,
        topic=topic,
        batch_size=batch_size,
        max_requests=max_requests,
    )


def send_message(
    to: Union[str, list[int], list[str]],
    content: str,
    type: str = "stream",
    topic: Optional[str] = None,
) -> int | None:
    """Send a message to a stream or private recipient."""

    return operations.send_message(to=to, content=content, type=type, topic=topic)


def react(message_id: int, emoji_name: str, reaction_type: str = "unicode") -> bool:
    """Add an emoji reaction to a Zulip message."""

    return operations.react(message_id=message_id, emoji_name=emoji_name, reaction_type=reaction_type)


def upload_file(file_path: str) -> str:
    """Upload a file to Zulip and return the uploaded URI."""

    return operations.upload_file(file_path)


def register(mcp: FastMCP) -> None:
    """Register Zulip tools with a FastMCP server."""

    mcp.tool(name="zulip_list_streams", tags=["zulip", "read"])(list_streams)
    mcp.tool(name="zulip_list_topics", tags=["zulip", "read"])(list_topics)
    mcp.tool(name="zulip_get_messages", tags=["zulip", "read"])(get_messages)
    mcp.tool(name="zulip_get_topic_messages", tags=["zulip", "read"])(get_topic_messages)
    mcp.tool(name="zulip_send_message", tags=["zulip", "write"])(send_message)
    mcp.tool(name="zulip_react", tags=["zulip", "write"])(react)
    mcp.tool(name="zulip_upload_file", tags=["zulip", "write"])(upload_file)


__all__ = [
    "get_messages",
    "get_topic_messages",
    "list_streams",
    "list_topics",
    "react",
    "register",
    "send_message",
    "upload_file",
]
