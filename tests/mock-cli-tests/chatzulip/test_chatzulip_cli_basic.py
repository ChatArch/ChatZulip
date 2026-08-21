from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from chatzulip import __version__
from chatzulip.cli import main


class FakeClient:
    site = "https://leanprover.zulipchat.com"

    def list_subscriptions(self):
        return [{"name": "general", "stream_id": 1, "description": "General chat"}]

    def list_streams(self, include_public=True):
        return [{"name": "general", "stream_id": 1, "description": "General chat"}]

    def list_topics(self, stream_id):
        assert stream_id == 1
        return [{"name": "release", "max_id": 42}]

    def get_messages(self, anchor="newest", num_before=20, num_after=0, narrow=None):
        return [
            {
                "id": 7,
                "timestamp": 1710000000,
                "display_recipient": "general",
                "subject": "release",
                "sender_full_name": "rex",
                "content": "ship it",
            }
        ]

    def get_topic_messages(self, stream, topic, batch_size=200, max_requests=200):
        assert stream == "general"
        assert topic == "release"
        return [
            {
                "timestamp": 1710000000,
                "sender_full_name": "rex",
                "content": "ship it",
            }
        ]

    def get_profile(self):
        return {"email": "bot@example.com", "full_name": "Zulip Bot", "user_id": 123}


def test_version_option_reports_package_version():
    result = CliRunner().invoke(main, ["--version"])

    assert result.exit_code == 0
    assert f"chatzulip, version {__version__}" in result.output


def test_help_exposes_full_and_brief_trees_and_no_template_hello():
    result = CliRunner().invoke(main, ["--help"])

    assert result.exit_code == 0
    assert "--tree" in result.output
    assert "--tree-brief" in result.output
    assert "hello" not in result.output.lower()


def test_tree_option_renders_registered_zulip_commands_with_signatures():
    result = CliRunner().invoke(main, ["--tree"])

    assert result.exit_code == 0, result.output
    assert result.output.splitlines()[0] == "chatzulip"
    assert "--help  # Show this message and exit." in result.output
    assert "--version  # Show the version and exit." in result.output
    assert "--tree  # Print the registered CLI tree and exit." in result.output
    assert (
        "--tree-brief  # Print the registered CLI tree without parameter signatures and exit."
        in result.output
    )
    for command in (
        "streams",
        "topics",
        "search-topics",
        "search",
        "messages",
        "topic",
        "profile",
        "news",
    ):
        assert command in result.output
    assert "search <QUERY>" in result.output
    assert "[--stream STREAMS]" in result.output
    assert "[--all-streams]" in result.output
    assert "[--interactive]" in result.output
    assert "hello" not in result.output.lower()


def test_tree_brief_keeps_nodes_and_descriptions_but_omits_signatures():
    full = CliRunner().invoke(main, ["--tree"])
    brief = CliRunner().invoke(main, ["--tree-brief"])

    assert full.exit_code == 0, full.output
    assert brief.exit_code == 0, brief.output
    assert brief.output.splitlines()[0] == "chatzulip"
    for description in (
        "List streams, subscribed by default.",
        "List topics for a stream.",
        "Search topic names across explicitly selected public streams.",
        "Search message content using stream-scoped Zulip narrows.",
        "Fetch messages with optional Zulip narrow filters.",
        "Export a full stream/topic thread.",
        "Show the authenticated bot/user profile.",
        "Render recent Zulip updates to Markdown.",
    ):
        assert description in full.output
        assert description in brief.output
    assert "<QUERY>" in full.output
    assert "[--stream STREAMS]" in full.output
    assert "[--interactive]" in full.output
    assert "<QUERY>" not in brief.output
    assert "[--stream STREAMS]" not in brief.output
    assert "[--interactive]" not in brief.output


def test_tree_root_uses_public_console_command_in_module_mode():
    result = CliRunner().invoke(main, ["--tree"], prog_name="python -m chatzulip.cli")

    assert result.exit_code == 0, result.output
    assert result.output.splitlines()[0] == "chatzulip"
    assert "python -m chatzulip.cli" not in result.output


def test_bilingual_cli_tree_docs_embed_the_registered_full_tree():
    result = CliRunner().invoke(main, ["--tree"])

    assert result.exit_code == 0, result.output
    documented_tree = f"```text\n{result.output.rstrip()}\n```"
    for doc in (Path("docs/cli-tree.md"), Path("docs/cli-tree.en.md")):
        assert documented_tree in doc.read_text(encoding="utf-8")


def test_streams_outputs_subscriptions(monkeypatch):
    monkeypatch.setattr("chatzulip.cli._get_client", lambda: FakeClient())

    result = CliRunner().invoke(main, ["streams"])

    assert result.exit_code == 0
    assert "general (id=1)" in result.output


def test_topics_outputs_stream_topics(monkeypatch):
    monkeypatch.setattr("chatzulip.cli._get_client", lambda: FakeClient())

    result = CliRunner().invoke(main, ["topics", "--stream", "general"])

    assert result.exit_code == 0
    assert "release (max_id=42)" in result.output


def test_topics_errors_with_no_interaction():
    result = CliRunner().invoke(main, ["topics", "-I"])

    assert result.exit_code != 0
    assert "Missing required value: stream" in result.output


def test_topic_exports_markdown(monkeypatch):
    monkeypatch.setattr("chatzulip.cli._get_client", lambda: FakeClient())

    result = CliRunner().invoke(main, ["topic", "--stream", "general", "--topic", "release"])

    assert result.exit_code == 0
    assert "# general / release" in result.output
    assert "ship it" in result.output


def test_messages_outputs_json(monkeypatch):
    monkeypatch.setattr("chatzulip.cli._get_client", lambda: FakeClient())

    result = CliRunner().invoke(main, ["messages", "--stream", "general", "--json-output"])

    assert result.exit_code == 0
    assert '"display_recipient": "general"' in result.output


def test_search_topics_outputs_cross_stream_results(monkeypatch):
    monkeypatch.setattr("chatzulip.cli._get_client", lambda: FakeClient())

    result = CliRunner().invoke(
        main,
        ["search-topics", "release", "--stream", "general", "--json-output"],
    )

    assert result.exit_code == 0
    assert '"topic": "release"' in result.output
    assert '"url": "https://leanprover.zulipchat.com/' in result.output


def test_search_outputs_stream_scoped_messages(monkeypatch):
    monkeypatch.setattr("chatzulip.cli._get_client", lambda: FakeClient())

    result = CliRunner().invoke(
        main,
        ["search", "ship", "--stream", "general", "--json-output"],
    )

    assert result.exit_code == 0
    assert '"id": 7' in result.output
    assert '"url": "https://leanprover.zulipchat.com/' in result.output


def test_search_requires_explicit_stream_scope():
    result = CliRunner().invoke(main, ["search", "ship"])

    assert result.exit_code != 0
    assert "Pass --stream at least once or use --all-streams" in result.output


def test_profile_outputs_identity(monkeypatch):
    monkeypatch.setattr("chatzulip.cli._get_client", lambda: FakeClient())

    result = CliRunner().invoke(main, ["profile"])

    assert result.exit_code == 0
    assert "Zulip Bot <bot@example.com> (id=123)" in result.output


def test_news_writes_markdown_with_rule_based_fallback(monkeypatch, tmp_path):
    monkeypatch.setattr("chatzulip.cli._get_client", lambda: FakeClient())
    monkeypatch.setattr(
        "chatzulip.operations.llm_summarize",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("LLM unavailable")),
    )
    output_path = tmp_path / "zulip-news.md"

    result = CliRunner().invoke(
        main,
        ["news", "--stream", "general", "--since-hours", "999999", "--output", str(output_path)],
    )

    assert result.exit_code == 0
    assert output_path.exists()
    content = output_path.read_text(encoding="utf-8")
    assert "Zulip News" in content
    assert "Rule-based summary" in content
    assert "LLM summary failed" in result.output
