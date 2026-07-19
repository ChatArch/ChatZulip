# test_zulip_client

Code tests for `chatzulip.client.ZulipClient` and `chatzulip.config.ZulipConfig`.

## Scope

- ChatEnv provider aliases and sensitive field metadata
- Zulip API parameter serialization
- clean missing-credential failure
- request path and query/form payload construction with a fake HTTP client

## Acceptance

- Credentials are never printed.
- Lists, dictionaries, booleans, and numbers are JSON-encoded for Zulip REST parameters.
- A client cannot be constructed without `ZULIP_SITE`, `ZULIP_BOT_EMAIL`, and `ZULIP_BOT_API_KEY` from explicit args, ChatEnv, or environment.
