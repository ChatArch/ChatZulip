# 开发计划

这个页面记录 `ChatZulip` 的能力边界和后续路线。

## Review Contract

- CLI 命令必须调用可 import 的 Python API。
- 文档先写已实现和已验证能力；未实现能力必须标记为未实现。
- 敏感信息不得进入 README、docs、issue、PR 评论或 CI log。
- CLI root 必须保持显式 `chatzulip` 名称，并由 ChatStyle 暴露 registry-backed `--tree` / `--tree-brief`。
- 写操作进入 CLI 前需要单独设计确认、权限和真实服务验证。

## Phase 1：当前已实现能力

```text
ChatTool Zulip capability extraction
├── ChatEnv provider: zulip / Zulip
├── REST client: streams, topics, messages, topic history, profile, send, react, upload
├── CLI: streams, topics, search-topics, search, topic, messages, profile, news
├── Operations API: importable functions for CLI/MCP reuse
└── MCP adapter: read/write tool registration functions
```

## Phase 2：下一步计划

```text
0.1.x release gates
├── Open ChatZulip feature PR
├── Merge after review and CI
├── Tag v0.1.0 from merged main through Trusted Publisher
└── Clean-install verify PyPI release

ChatTool parent cleanup
├── Remove chattool zulip command implementation
├── Remove parent Zulip config re-export if no longer needed
├── Retarget optional extra to ChatZulip>=0.1.0,<0.2.0
└── Update docs/tests/changelog and open separate ChatTool PR
```
