"""Zulip API client."""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any, Optional, Union

from chatenv import EnvStore, get_paths

from .config import ZulipConfig

JsonDict = dict[str, Any]


class ZulipClient:
    """Small synchronous Zulip REST client.

    The client mirrors the parameter serialization used by Zulip's official
    Python SDK while keeping ChatArch configuration in ChatEnv.
    """

    def __init__(
        self,
        *,
        site: str | None = None,
        bot_email: str | None = None,
        bot_api_key: str | None = None,
        timeout: float = 30.0,
        env_profile: str | None = None,
        chatarch_home: str | Path | None = None,
        http_client: Any | None = None,
    ) -> None:
        self.logger = logging.getLogger("chatzulip.client")
        values = self._load_config_values(env_profile=env_profile, chatarch_home=chatarch_home)
        self.site = site or values.get("ZULIP_SITE") or ZulipConfig.ZULIP_SITE.value
        self.email = bot_email or values.get("ZULIP_BOT_EMAIL") or ZulipConfig.ZULIP_BOT_EMAIL.value
        self.api_key = (
            bot_api_key
            or values.get("ZULIP_BOT_API_KEY")
            or ZulipConfig.ZULIP_BOT_API_KEY.value
        )

        if not all([self.site, self.email, self.api_key]):
            raise ValueError(
                "Missing Zulip credentials. Configure ZULIP_SITE, "
                "ZULIP_BOT_EMAIL, and ZULIP_BOT_API_KEY in ChatEnv or environment."
            )

        self.base_url = str(self.site).rstrip("/") + "/api/v1"
        self.auth = (self.email, self.api_key)
        if http_client is not None:
            self.client = http_client
        else:
            import httpx

            self.client = httpx.Client(auth=self.auth, timeout=timeout)

    @staticmethod
    def _load_config_values(
        *, env_profile: str | None = None, chatarch_home: str | Path | None = None
    ) -> dict[str, str]:
        try:
            store = EnvStore(get_paths(chatarch_home).envs_dir)
            values = (
                store.load_profile(ZulipConfig, env_profile)
                if env_profile
                else store.load_active(ZulipConfig)
            )
        except Exception:
            values = {}
        if env_profile:
            values = {
                field.env_key: values.get(
                    field.env_key,
                    field.default if field.default is not None else "",
                )
                for field in ZulipConfig.get_fields().values()
            }
            ZulipConfig.load_from_sources(override_values=values)
            return values
        ZulipConfig.load_from_sources(env_values=values)
        return values

    @staticmethod
    def _prepare_params(params: JsonDict) -> dict[str, str]:
        """Prepare Zulip form/query parameters.

        Zulip expects strings as-is and JSON-encoded values for lists, dicts,
        booleans, and numbers in many REST parameters.
        """

        prepared: dict[str, str] = {}
        for key, value in params.items():
            if value is None:
                continue
            prepared[key] = value if isinstance(value, str) else json.dumps(value)
        return prepared

    def _request(
        self,
        method: str,
        endpoint: str,
        params: JsonDict | None = None,
        files: dict[str, Any] | None = None,
    ) -> JsonDict:
        url = f"{self.base_url}{endpoint}"
        kwargs: dict[str, Any] = {}
        if params:
            prepared_params = self._prepare_params(params)
            if method.upper() == "GET":
                kwargs["params"] = prepared_params
            else:
                kwargs["data"] = prepared_params
        if files:
            kwargs["files"] = files

        import httpx

        try:
            response = self.client.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            self.logger.error("HTTP error %s: %s", exc.response.status_code, exc.response.text)
            raise RuntimeError(
                f"Zulip API error ({exc.response.status_code}): {exc.response.text}"
            ) from exc
        except Exception:
            self.logger.exception("Zulip request failed")
            raise

    def send_message(
        self,
        type: str,
        to: Union[str, list[int], list[str]],
        content: str,
        topic: Optional[str] = None,
    ) -> JsonDict:
        data: JsonDict = {"type": type, "to": to, "content": content}
        if topic:
            data["topic"] = topic
        return self._request("POST", "/messages", params=data)

    def get_messages(
        self,
        anchor: Union[int, str] = "newest",
        num_before: int = 20,
        num_after: int = 0,
        narrow: Optional[list[JsonDict]] = None,
    ) -> list[JsonDict]:
        params: JsonDict = {
            "anchor": anchor,
            "num_before": num_before,
            "num_after": num_after,
            "apply_markdown": False,
        }
        if narrow:
            params["narrow"] = narrow
        result = self._request("GET", "/messages", params=params)
        return result.get("messages", [])

    def list_streams(self, include_public: bool = True) -> list[JsonDict]:
        result = self._request("GET", "/streams", params={"include_public": include_public})
        return result.get("streams", [])

    def list_subscriptions(self) -> list[JsonDict]:
        result = self._request("GET", "/users/me/subscriptions")
        return result.get("subscriptions", [])

    def list_topics(self, stream_id: int) -> list[JsonDict]:
        result = self._request("GET", f"/users/me/{stream_id}/topics")
        return result.get("topics", [])

    def get_topic_messages(
        self,
        stream: Union[int, str],
        topic: str,
        batch_size: int = 200,
        max_requests: int = 200,
    ) -> list[JsonDict]:
        narrow = [
            {"operator": "stream", "operand": stream},
            {"operator": "topic", "operand": topic},
        ]
        all_messages: list[JsonDict] = []
        anchor: Union[int, str] = "newest"

        for _ in range(max_requests):
            result = self._request(
                "GET",
                "/messages",
                params={
                    "anchor": anchor,
                    "num_before": batch_size,
                    "num_after": 0,
                    "apply_markdown": False,
                    "narrow": narrow,
                },
            )
            messages = result.get("messages", [])
            if not messages:
                break
            all_messages = messages + all_messages
            if result.get("found_oldest"):
                break
            anchor = str(messages[0]["id"])

        all_messages.sort(key=lambda item: item.get("id", 0))
        return all_messages

    def react_to_message(
        self, message_id: int, emoji_name: str, reaction_type: str = "unicode"
    ) -> JsonDict:
        return self._request(
            "POST",
            f"/messages/{message_id}/reactions",
            params={"emoji_name": emoji_name, "reaction_type": reaction_type},
        )

    def get_profile(self) -> JsonDict:
        return self._request("GET", "/users/me")

    def upload_file(self, file_path: str) -> str:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, "rb") as handle:
            response = self.client.post(f"{self.base_url}/user_uploads", files={"file": handle})
            response.raise_for_status()
            result = response.json()
        return result.get("uri")


__all__ = ["JsonDict", "ZulipClient"]
