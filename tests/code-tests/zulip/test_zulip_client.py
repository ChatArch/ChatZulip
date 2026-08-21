from __future__ import annotations

import pytest
from chatenv import EnvStore, get_paths

from chatzulip.client import ZulipClient
from chatzulip.config import ZulipConfig


class FakeResponse:
    def __init__(self, data, status_code=200, text="OK"):
        self._data = data
        self.status_code = status_code
        self.text = text

    def raise_for_status(self):
        return None

    def json(self):
        return self._data


class FakeHttpClient:
    def __init__(self):
        self.calls = []

    def request(self, method, url, **kwargs):
        self.calls.append((method, url, kwargs))
        return FakeResponse({"messages": [{"id": 1}]})

    def post(self, url, files=None):
        self.calls.append(("POST", url, {"files": bool(files)}))
        return FakeResponse({"uri": "/user_uploads/example.txt"})


def test_config_exposes_zulip_service_fields():
    assert ZulipConfig._aliases == ["zulip", "chatzulip"]
    assert ZulipConfig._storage_dir == "Zulip"
    assert ZulipConfig.ZULIP_BOT_API_KEY.is_sensitive is True
    assert ZulipConfig.ZULIP_NEWS_SINCE_HOURS.default == "24"


def test_prepare_params_json_encodes_non_strings():
    params = ZulipClient._prepare_params(
        {"stream": "general", "narrow": [{"operator": "stream", "operand": "general"}], "flag": True}
    )

    assert params["stream"] == "general"
    assert params["narrow"] == '[{"operator": "stream", "operand": "general"}]'
    assert params["flag"] == "true"


def test_missing_credentials_fail_cleanly(tmp_path, monkeypatch):
    for key in ["ZULIP_SITE", "ZULIP_BOT_EMAIL", "ZULIP_BOT_API_KEY"]:
        monkeypatch.delenv(key, raising=False)

    with pytest.raises(ValueError, match="Missing Zulip credentials"):
        ZulipClient(chatarch_home=tmp_path)


def test_named_profile_uses_typed_chatenv_storage_and_ignores_process_credentials(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setenv("ZULIP_SITE", "https://process.zulipchat.com")
    monkeypatch.setenv("ZULIP_BOT_EMAIL", "process@example.com")
    monkeypatch.setenv("ZULIP_BOT_API_KEY", "process-secret")
    store = EnvStore(get_paths(tmp_path).envs_dir)
    profile_path = store.save_profile(
        ZulipConfig,
        "work",
        {
            "ZULIP_SITE": "https://profile.zulipchat.com",
            "ZULIP_BOT_EMAIL": "profile@example.com",
            "ZULIP_BOT_API_KEY": "profile-secret",
        },
    )

    client = ZulipClient(
        env_profile="work",
        chatarch_home=tmp_path,
        http_client=FakeHttpClient(),
    )

    assert profile_path == tmp_path / "envs" / "Zulip" / "work.env"
    assert client.site == "https://profile.zulipchat.com"
    assert client.email == "profile@example.com"
    assert client.api_key == "profile-secret"


def test_named_profile_does_not_backfill_missing_secret_from_process_env(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setenv("ZULIP_BOT_API_KEY", "process-secret")
    store = EnvStore(get_paths(tmp_path).envs_dir)
    store.save_profile(
        ZulipConfig,
        "work",
        {
            "ZULIP_SITE": "https://profile.zulipchat.com",
            "ZULIP_BOT_EMAIL": "profile@example.com",
        },
    )

    with pytest.raises(ValueError, match="Missing Zulip credentials"):
        ZulipClient(
            env_profile="work",
            chatarch_home=tmp_path,
            http_client=FakeHttpClient(),
        )


def test_get_messages_uses_zulip_api_params():
    fake = FakeHttpClient()
    client = ZulipClient(
        site="https://example.zulipchat.com",
        bot_email="bot@example.com",
        bot_api_key="secret",
        http_client=fake,
    )

    messages = client.get_messages(narrow=[{"operator": "stream", "operand": "general"}])

    assert messages == [{"id": 1}]
    method, url, kwargs = fake.calls[0]
    assert method == "GET"
    assert url == "https://example.zulipchat.com/api/v1/messages"
    assert kwargs["params"]["narrow"] == '[{"operator": "stream", "operand": "general"}]'
