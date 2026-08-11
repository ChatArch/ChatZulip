# CLI 能力地图

`ChatZulip` 提供从 ChatTool 迁移出的 Zulip 集成 CLI。CLI 是薄适配层，核心逻辑位于 `chatzulip.operations` 和 `chatzulip.client`。

## 当前命令树

运行时可用 `chatzulip --tree` 读取真实注册的 Click command surface。`--tree` 输出从 CLI registry 生成，不手写 README 示例。

```text
chatzulip # Zulip helpers for ChatArch workflows
├── --help # Show this message and exit
├── --version # Show the version and exit
├── --tree # Print the registered command tree
├── streams [--all] [--json-output] # List streams, subscribed by default
├── topics [--stream STREAM] [--json-output] [--interactive] # List topics for a stream
├── search-topics QUERY [--stream STREAMS] [--all-streams] [--limit LIMIT] [--json-output] # Search topic names across explicitly selected public streams
├── search QUERY [--stream STREAMS] [--all-streams] [--since-hours SINCE-HOURS] [--per-stream PER-STREAM] [--limit LIMIT] [--json-output] # Search message content using stream-scoped Zulip narrows
├── messages [--anchor ANCHOR] [--before NUM-BEFORE] [--after NUM-AFTER] [--stream STREAM] [--topic TOPIC] [--sender SENDER] [--search SEARCH] [--json-output] # Fetch messages with optional Zulip narrow filters
├── topic [--stream STREAM] [--topic TOPIC-NAME] [--batch-size BATCH-SIZE] [--max-requests MAX-REQUESTS] [--output OUTPUT] [--json-output] [--interactive] # Export a full stream/topic thread
├── profile [--json-output] # Show the authenticated bot/user profile
└── news [--stream STREAMS] [--topic TOPICS] [--since-hours SINCE-HOURS] [--per-stream PER-STREAM] [--limit LIMIT] [--output OUTPUT] [--model MODEL] [--max-tokens MAX-TOKENS] [--temperature TEMPERATURE] # Render recent Zulip updates to Markdown
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
