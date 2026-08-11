from __future__ import annotations

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


def test_help_exposes_tree_and_no_template_hello():
    result = CliRunner().invoke(main, ["--help"])

    assert result.exit_code == 0
    assert "--tree" in result.output
    assert "hello" not in result.output.lower()


def test_tree_option_renders_registered_zulip_commands_and_no_template_hello():
    result = CliRunner().invoke(main, ["--tree"])

    assert result.exit_code == 0
    assert "chatzulip" in result.output
    assert "--help" in result.output
    assert "--version" in result.output
    assert "--tree" in result.output
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
    assert "hello" not in result.output.lower()


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
