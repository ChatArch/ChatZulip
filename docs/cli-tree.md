# CLI 能力地图

`ChatZulip` 提供从 ChatTool 迁移出的 Zulip 集成 CLI。CLI 是薄适配层，核心逻辑位于 `chatzulip.operations` 和 `chatzulip.client`。

## 当前命令树

```text
chatzulip --version                         # 显示包版本
chatzulip streams [--all] [--json-output]   # 列出已订阅或可访问 streams
chatzulip topics --stream TEXT              # 列出某个 stream 的 topics
chatzulip search-topics QUERY [scope...]    # 跨选定/全部公开 streams 搜 topic 名
chatzulip search QUERY [scope...]           # 用 stream-scoped narrow 搜消息内容
chatzulip topic --stream TEXT --topic TEXT  # 导出完整 topic thread
chatzulip messages [filters...]             # 按 Zulip narrow 条件获取消息
chatzulip profile [--json-output]           # 显示当前 bot/user profile
chatzulip news [filters...] [--output PATH] # 生成近期消息 Markdown 摘要
```

`search-topics` 和 `search` 要求显式传入至少一个可重复的 `--stream`，或显式使用 `--all-streams`。后者会对每个可访问公开 stream 发起 API 请求，因此不会作为隐式默认。`search` 还支持 `--since-hours`、`--per-stream` 和全局 `--limit`；搜索结果包含可直接打开的 Zulip permalink。

## 配置

ChatZulip 使用 ChatEnv 的 `zulip` provider，字段名沿用 Zulip 服务语义：

```text
ZULIP_SITE
ZULIP_BOT_EMAIL
ZULIP_BOT_API_KEY
ZULIP_NEWS_STREAMS
ZULIP_NEWS_TOPICS
ZULIP_NEWS_SINCE_HOURS
ZULIP_NEWS_PER_STREAM
```

`ZULIP_BOT_API_KEY` 是敏感字段；CLI 输出和文档示例不应打印真实值。

## Python API 对应关系

| CLI | Python API |
| --- | --- |
| `streams` | `chatzulip.operations.list_streams()` |
| `topics` | `chatzulip.operations.list_topics()` |
| `search-topics` | `chatzulip.operations.search_topics()` |
| `search` | `chatzulip.operations.search_messages()` |
| `topic` | `chatzulip.operations.get_topic_messages()` + `render_topic_markdown()` |
| `messages` | `chatzulip.operations.get_messages()` |
| `profile` | `chatzulip.client.ZulipClient.get_profile()` |
| `news` | `chatzulip.operations.summarize_news()` |

`chatzulip news` 默认会尝试使用可选 `chattool` LLM summarizer；没有安装 `chatzulip[llm]` 或当前环境不可用时，会自动降级为 rule-based Markdown 摘要。

## 写操作边界

第一版 CLI 保持从 ChatTool 迁移来的 read-oriented 命令面。写操作通过 importable API 和 MCP adapter 暴露：

- `chatzulip.operations.send_message()`
- `chatzulip.operations.react()`
- `chatzulip.operations.upload_file()`
- `chatzulip.mcp.register()`

未来如果要把写操作放入 CLI，应单独设计确认、dry-run、权限和真实 Zulip smoke 测试。
