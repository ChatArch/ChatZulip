from __future__ import annotations

from chatzulip import operations


class FakeClient:
    site = "https://leanprover.zulipchat.com"

    def list_subscriptions(self):
        return [{"name": "general", "stream_id": 1}]

    def list_streams(self, include_public=True):
        return [{"name": "general", "stream_id": 1}]

    def list_topics(self, stream_id):
        return [{"name": "release", "max_id": 42}]

    def get_messages(self, anchor="newest", num_before=20, num_after=0, narrow=None):
        return [
            {
                "id": 1,
                "timestamp": 1710000000,
                "display_recipient": "general",
                "subject": "release",
                "sender_full_name": "rex",
                "content": "ship it",
            }
        ]

    def get_topic_messages(self, stream, topic, batch_size=200, max_requests=200):
        return [{"id": 1, "timestamp": 1710000000, "sender_full_name": "rex", "content": "ship it"}]

    def send_message(self, type, to, content, topic=None):
        return {"result": "success", "id": 99}

    def react_to_message(self, message_id, emoji_name, reaction_type="unicode"):
        return {"result": "success"}

    def upload_file(self, file_path):
        return "/user_uploads/example.txt"


class AllStreamsClient(FakeClient):
    def list_streams(self, include_public=True):
        return [
            {"name": "general", "stream_id": 1, "invite_only": False},
            {"name": "lean4", "stream_id": 2, "invite_only": False},
            {"name": "private", "stream_id": 3, "invite_only": True},
        ]

    def list_topics(self, stream_id):
        if stream_id in {2, 3}:
            return [{"name": "Counterexample to the Lean Conjecture", "max_id": 99}]
        return [{"name": "release", "max_id": 42}]


def test_build_narrow_filters_empty_values():
    assert operations.build_narrow(stream="general", topic="release") == [
        {"operator": "stream", "operand": "general"},
        {"operator": "topic", "operand": "release"},
    ]
    assert operations.build_narrow() is None


def test_resolve_stream_id_from_subscription():
    assert operations.resolve_stream_id(FakeClient(), "general") == 1
    assert operations.resolve_stream_id(FakeClient(), "42") == 42


def test_render_topic_markdown():
    markdown = operations.render_topic_markdown(
        "general",
        "release",
        [{"timestamp": 1710000000, "sender_full_name": "rex", "content": "ship it"}],
    )

    assert markdown.startswith("# general / release")
    assert "ship it" in markdown


def test_topic_permalink_uses_zulip_narrow_encoding():
    url = operations.topic_permalink(
        "https://leanprover.zulipchat.com",
        stream_id=270676,
        stream="lean4",
        topic="Counterexample to the Lean Conjecture (Soundness Bug)",
        near=613135216,
    )

    assert "Counterexample.20to.20the.20Lean.20Conjecture.20.28Soundness.20Bug.29" in url
    assert url.endswith("/near/613135216")


def test_search_topics_returns_normalized_matches_with_urls():
    matches = operations.search_topics("LEASE", streams=["general"], client=FakeClient())

    assert matches == [
        {
            "stream": "general",
            "stream_id": 1,
            "topic": "release",
            "max_id": 42,
            "url": (
                "https://leanprover.zulipchat.com/#narrow/channel/1-general/"
                "topic/release/near/42"
            ),
        }
    ]


def test_search_topics_can_discover_unsubscribed_public_streams():
    matches = operations.search_topics(
        "conjecture",
        all_streams=True,
        client=AllStreamsClient(),
    )

    assert [(item["stream"], item["topic"]) for item in matches] == [
        ("lean4", "Counterexample to the Lean Conjecture")
    ]


def test_search_messages_scopes_to_stream_and_adds_permalink():
    matches = operations.search_messages("ship", streams=["general"], client=FakeClient())

    assert matches[0]["id"] == 1
    assert matches[0]["stream_id"] == 1
    assert matches[0]["url"].endswith("/topic/release/near/1")


def test_importable_message_operations():
    fake = FakeClient()

    assert operations.list_topics("general", fake)[0]["name"] == "release"
    assert operations.get_messages(stream="general", client=fake)[0]["id"] == 1
    assert operations.get_topic_messages("general", "release", client=fake)[0]["content"] == "ship it"
    assert operations.send_message(to="general", content="hello", topic="release", client=fake) == 99
    assert operations.react(message_id=1, emoji_name="thumbs_up", client=fake) is True
    assert operations.upload_file("example.txt", client=fake) == "/user_uploads/example.txt"


def test_summarize_news_writes_output_with_fallback(monkeypatch, tmp_path):
    monkeypatch.setattr(
        operations,
        "llm_summarize",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("LLM unavailable")),
    )
    output_path = tmp_path / "news.md"

    result = operations.summarize_news(
        streams=["general"],
        since_hours=999999,
        output=str(output_path),
        client=FakeClient(),
    )

    assert result.used_fallback is True
    assert output_path.exists()
    assert "Rule-based summary" in result.markdown
