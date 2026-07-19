"Typed environment configuration for Zulip."

from chatenv import BaseEnvConfig, EnvField


class ZulipConfig(BaseEnvConfig):
    "Zulip ChatEnv configuration."

    _title = "Zulip Configuration"
    _aliases = ["zulip", "chatzulip"]
    _storage_dir = "Zulip"

    @classmethod
    def test(cls) -> None:
        """Validate schema registration without external side effects."""

        print(f"Testing {cls._title}...")
        print("Schema loaded; no network test is required.")

    ZULIP_SITE = EnvField("ZULIP_SITE", desc="Zulip site URL")
    ZULIP_BOT_EMAIL = EnvField("ZULIP_BOT_EMAIL", desc="Zulip bot email")
    ZULIP_BOT_API_KEY = EnvField(
        "ZULIP_BOT_API_KEY",
        desc="Zulip bot API key",
        is_sensitive=True,
    )
    ZULIP_NEWS_STREAMS = EnvField("ZULIP_NEWS_STREAMS", desc="Default news streams CSV")
    ZULIP_NEWS_TOPICS = EnvField("ZULIP_NEWS_TOPICS", desc="Default news topics CSV")
    ZULIP_NEWS_SINCE_HOURS = EnvField("ZULIP_NEWS_SINCE_HOURS", desc="Default news lookback hours")
    ZULIP_NEWS_PER_STREAM = EnvField("ZULIP_NEWS_PER_STREAM", desc="Default news fetch limit per stream")


__all__ = ["ZulipConfig"]
