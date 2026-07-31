# ChatZulip Docs

ChatZulip is the ChatArch Zulip integration package. The current functional version extracts the Zulip client, read-oriented CLI, Markdown news digest, and MCP adapter from `ChatTool` into a standalone package while keeping the follow-up `ChatTool` parent-removal boundary explicit.

## Choose By Scenario

| Scenario | Document |
| --- | --- |
| Understand package identity, configuration boundaries, release gates, and parent migration order | [ChatZulip Specification](specification.en.md) |
| Install the package, run the CLI, and confirm it works | [CLI Capability Map](cli-tree.md) |
| Call package behavior directly from Python | [Python Interface Tree](interface-tree.md) |
| Record implemented, verified, and planned capability boundaries | [Development Plan](development-plan.md) |

## Current Capability Summary

- ChatEnv provider: `zulip`, with `ZULIP_*` service-oriented fields.
- CLI: `streams`, `topics`, `search-topics`, `search`, `topic`, `messages`, `profile`, and `news`.
- Python API: `ZulipClient` and `chatzulip.operations`.
- MCP adapter: `chatzulip.mcp.register()`.
- Write operations: available as Python/MCP capabilities, not default CLI commands yet.

## Documentation Status

- **Implemented**: code, tests, or CLI routes exist.
- **Verified**: covered by local smoke, CI, or real-service practice.
- **Not implemented**: keep as roadmap and safety notes only; turn into operation docs after implementation and validation.

## Local Preview

```bash
python -m pip install -e ".[docs]"
mkdocs serve
```

The Chinese home page is available at <https://arch.gh.wzhecnu.cn/ChatZulip/>. Topic pages without English translations fall back to the default Chinese content through the i18n plugin.
