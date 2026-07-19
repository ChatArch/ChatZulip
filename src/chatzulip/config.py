"""Typed environment configuration for Zulip."""

from __future__ import annotations

from chatenv import BaseEnvConfig, EnvField


class ZulipConfig(BaseEnvConfig):
    """Zulip ChatEnv configuration."""

    _title = "Zulip Configuration"
    _aliases = ["zulip", "chatzulip"]
    _storage_dir = "Zulip"

    ZULIP_SITE = EnvField("ZULIP_SITE", desc="Zulip site URL")
    ZULIP_BOT_EMAIL = EnvField("ZULIP_BOT_EMAIL", desc="Zulip bot email")
    ZULIP_BOT_API_KEY = EnvField(
        "ZULIP_BOT_API_KEY",
        desc="Zulip bot API key",
        is_sensitive=True,
    )
    ZULIP_NEWS_STREAMS = EnvField(
        "ZULIP_NEWS_STREAMS",
        desc="Comma-separated stream names for news summary",
    )
    ZULIP_NEWS_TOPICS = EnvField(
        "ZULIP_NEWS_TOPICS",
        desc="Comma-separated topic names for news summary",
    )
    ZULIP_NEWS_SINCE_HOURS = EnvField(
        "ZULIP_NEWS_SINCE_HOURS",
        default="24",
        desc="Default hours for news window",
    )
    ZULIP_NEWS_PER_STREAM = EnvField(
        "ZULIP_NEWS_PER_STREAM",
        default="200",
        desc="Default per-stream fetch limit for news",
    )

    @classmethod
    def test(cls) -> None:
        """Validate schema registration without external side effects."""

        print(f"Testing {cls._title}...")
        print("Schema loaded; use chatzulip profile to verify live credentials.")


__all__ = ["ZulipConfig"]
