"""CLI entrypoint for chatzulip."""

from __future__ import annotations

import json
from typing import Any

import click
from chatstyle import CommandField, CommandSchema, add_interactive_option, resolve_command_inputs

from chatzulip import __version__
from chatzulip import operations
from chatzulip.client import ZulipClient

ZULIP_STREAM_SCHEMA = CommandSchema(
    name="zulip-stream",
    fields=(CommandField("stream", prompt="stream", required=True),),
)

ZULIP_TOPIC_SCHEMA = CommandSchema(
    name="zulip-topic",
    fields=(
        CommandField("stream", prompt="stream", required=True),
        CommandField("topic_name", prompt="topic", required=True),
    ),
)


def _get_client() -> ZulipClient:
    try:
        return ZulipClient()
    except Exception as exc:
        raise click.ClickException(str(exc)) from exc


def _echo_json(value: Any) -> None:
    click.echo(json.dumps(value, ensure_ascii=False, indent=2))


@click.group()
@click.version_option(__version__, prog_name="chatzulip")
def main() -> None:
    """Zulip helpers for ChatArch workflows."""


@main.command(name="streams")
@click.option("--all", "show_all", is_flag=True, help="Show all accessible public streams")
@click.option("--json-output", is_flag=True, help="Output JSON")
def streams(show_all: bool, json_output: bool) -> None:
    """List streams, subscribed by default."""

    try:
        items = operations.list_streams(_get_client(), include_public=show_all)
    except Exception as exc:
        raise click.ClickException(str(exc)) from exc

    if json_output:
        _echo_json(items)
        return
    if not items:
        click.echo("No streams found.")
        return
    for item in items:
        name = item.get("name")
        stream_id = item.get("stream_id")
        desc = item.get("description", "")
        click.echo(f"- {name} (id={stream_id})")
        if desc:
            click.echo(f"  {desc}")


@main.command(name="topics")
@click.option("--stream", required=False, help="Stream name or id")
@click.option("--json-output", is_flag=True, help="Output JSON")
@add_interactive_option
def topics(stream: str | None, json_output: bool, interactive: bool | None) -> None:
    """List topics for a stream."""

    inputs = resolve_command_inputs(
        schema=ZULIP_STREAM_SCHEMA,
        provided={"stream": stream},
        interactive=interactive,
        usage="Usage: chatzulip topics --stream TEXT [-i|-I]",
    )
    client = _get_client()
    try:
        items = operations.list_topics(inputs["stream"], client)
    except Exception as exc:
        raise click.ClickException(str(exc)) from exc

    if json_output:
        _echo_json(items)
        return
    if not items:
        click.echo("No topics found.")
        return
    for item in sorted(items, key=lambda value: value.get("max_id") or 0, reverse=True):
        click.echo(f"- {item.get('name')} (max_id={item.get('max_id')})")


@main.command(name="messages")
@click.option("--anchor", default="newest", help="Message anchor ID or newest/oldest")
@click.option("--before", "num_before", default=20, show_default=True, help="Messages before anchor")
@click.option("--after", "num_after", default=0, show_default=True, help="Messages after anchor")
@click.option("--stream", default=None, help="Filter by stream name")
@click.option("--topic", default=None, help="Filter by topic name")
@click.option("--sender", default=None, help="Filter by sender email")
@click.option("--search", default=None, help="Filter by search keyword")
@click.option("--json-output", is_flag=True, help="Output JSON")
def messages(
    anchor: str,
    num_before: int,
    num_after: int,
    stream: str | None,
    topic: str | None,
    sender: str | None,
    search: str | None,
    json_output: bool,
) -> None:
    """Fetch messages with optional Zulip narrow filters."""

    try:
        items = operations.get_messages(
            anchor=anchor,
            num_before=num_before,
            num_after=num_after,
            stream=stream,
            topic=topic,
            sender=sender,
            search=search,
            client=_get_client(),
        )
    except Exception as exc:
        raise click.ClickException(str(exc)) from exc

    if json_output:
        _echo_json(items)
        return
    click.echo(operations.render_messages(items) if items else "No messages found.")


@main.command(name="topic")
@click.option("--stream", required=False, help="Stream name or id")
@click.option("--topic", "topic_name", required=False, help="Topic name")
@click.option("--batch-size", default=200, show_default=True, help="Messages per API request")
@click.option("--max-requests", default=200, show_default=True, help="Maximum pagination requests")
@click.option("--output", default=None, help="Output Markdown path")
@click.option("--json-output", is_flag=True, help="Output raw JSON")
@add_interactive_option
def topic(
    stream: str | None,
    topic_name: str | None,
    batch_size: int,
    max_requests: int,
    output: str | None,
    json_output: bool,
    interactive: bool | None,
) -> None:
    """Export a full stream/topic thread."""

    inputs = resolve_command_inputs(
        schema=ZULIP_TOPIC_SCHEMA,
        provided={"stream": stream, "topic_name": topic_name},
        interactive=interactive,
        usage="Usage: chatzulip topic --stream TEXT --topic TEXT [-i|-I]",
    )
    stream_value = str(inputs["stream"])
    topic_value = str(inputs["topic_name"])
    try:
        items = operations.get_topic_messages(
            stream_value,
            topic_value,
            batch_size=batch_size,
            max_requests=max_requests,
            client=_get_client(),
        )
    except Exception as exc:
        raise click.ClickException(str(exc)) from exc

    if json_output:
        _echo_json(items)
        return
    markdown = operations.render_topic_markdown(stream_value, topic_value, items)
    if output:
        with open(output, "w", encoding="utf-8") as handle:
            handle.write(markdown)
        click.echo(f"Saved to {output}")
    else:
        click.echo(markdown, nl=False)


@main.command(name="profile")
@click.option("--json-output", is_flag=True, help="Output JSON")
def profile(json_output: bool) -> None:
    """Show the authenticated bot/user profile."""

    try:
        item = _get_client().get_profile()
    except Exception as exc:
        raise click.ClickException(str(exc)) from exc
    if json_output:
        _echo_json(item)
        return
    email = item.get("email") or "unknown"
    full_name = item.get("full_name") or item.get("full_name_or_email") or "unknown"
    user_id = item.get("user_id") or "unknown"
    click.echo(f"{full_name} <{email}> (id={user_id})")


@main.command(name="news")
@click.option("--stream", "streams", multiple=True, help="Specify stream; repeatable")
@click.option("--topic", "topics", multiple=True, help="Specify topic; repeatable")
@click.option("--since-hours", type=int, default=None, help="Look back N hours; default from ChatEnv or 24")
@click.option("--per-stream", type=int, default=None, help="Per-stream fetch limit")
@click.option("--limit", type=int, default=None, help="Global message cap, latest messages")
@click.option("--output", default=None, help="Output Markdown path")
@click.option("--model", default=None, help="Optional ChatTool LLM model override when available")
@click.option("--max-tokens", type=int, default=800, show_default=True, help="Summary max tokens")
@click.option("--temperature", type=float, default=0.2, show_default=True, help="Summary temperature")
def news(
    streams: tuple[str, ...],
    topics: tuple[str, ...],
    since_hours: int | None,
    per_stream: int | None,
    limit: int | None,
    output: str | None,
    model: str | None,
    max_tokens: int,
    temperature: float,
) -> None:
    """Render recent Zulip updates to Markdown."""

    try:
        result = operations.summarize_news(
            streams=list(streams),
            topics=list(topics),
            since_hours=since_hours,
            per_stream=per_stream,
            limit=limit,
            output=output,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            client=_get_client(),
        )
    except Exception as exc:
        raise click.ClickException(str(exc)) from exc
    if result.used_fallback and result.fallback_reason:
        click.echo(f"LLM summary failed, fell back to rule-based summary: {result.fallback_reason}", err=True)
    click.echo(f"Saved to {result.output_path}")
    click.echo(result.markdown)


if __name__ == "__main__":
    main()
