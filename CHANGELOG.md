# Changelog

## Unreleased

### Added

- Add explicit cross-stream `search-topics` and message `search` commands for bots that can read public stream history but are not subscribed to every stream.
- Add reusable Zulip topic/message permalink helpers and include canonical URLs in normalized search results.

## 0.1.0 - 2026-07-19

### Added

- Port Zulip client, read-only CLI commands, news rendering, and MCP adapters from ChatTool into ChatZulip.
- Add ChatEnv-backed Zulip configuration fields: `ZULIP_SITE`, `ZULIP_BOT_EMAIL`, `ZULIP_BOT_API_KEY`, and news defaults.
- Add importable operations behind CLI/MCP adapters for stream/topic/message/news workflows.

## 0.0.1 - 2026-07-19

### Added

- Initial placeholder package, CLI scaffold, ChatEnv provider, CI, docs, and Trusted Publisher release workflow.
