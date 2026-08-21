# Changelog

## Unreleased

## 0.1.2 - 2026-08-22

### Changed

- Replace the package-local CLI tree renderer with ChatStyle's registered Click tree runtime and add `chatzulip --tree-brief`.
- Require `chatstyle>=0.2.0,<0.3.0` and `chatenv>=0.2.10,<0.3.0`, preserving the typed `zulip` provider and canonical ChatEnv storage paths.
- Keep explicitly selected ChatEnv profiles isolated from process credentials when profile fields are missing.
- Verify Python 3.10-3.12, installed CLI trees, package artifacts, Twine metadata, and strict docs in CI.

## 0.1.1 - 2026-08-11

### Added

- Add top-level `chatzulip --tree` output generated from the registered Click command surface.
- Add MkDocs Material emoji renderer configuration so Material icon shorthand cannot leak to generated pages.
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
