# CLI Capability Map

`ChatZulip` provides the Zulip integration CLI extracted from ChatTool. The CLI is a thin adapter over `chatzulip.operations` and `chatzulip.client`.

## Registered command tree

Run `chatzulip --tree` for the real Click command surface with parameter signatures. `chatzulip --tree-brief` keeps the same nodes and descriptions without signatures. ChatStyle renders both directly from the CLI registry; ChatZulip does not maintain a local tree renderer.

```text
chatzulip
├── --help  # Show this message and exit.
├── --version  # Show the version and exit.
├── --tree  # Print the registered CLI tree and exit.
├── --tree-brief  # Print the registered CLI tree without parameter signatures and exit.
├── messages [--anchor ANCHOR] [--before NUM-BEFORE] [--after NUM-AFTER] [--stream STREAM] [--topic TOPIC] [--sender SENDER] [--search SEARCH] [--json-output]  # Fetch messages with optional Zulip narrow filters.
├── news [--stream STREAMS] [--topic TOPICS] [--since-hours SINCE-HOURS] [--per-stream PER-STREAM] [--limit LIMIT] [--output OUTPUT] [--model MODEL] [--max-tokens MAX-TOKENS] [--temperature TEMPERATURE]  # Render recent Zulip updates to Markdown.
├── profile [--json-output]  # Show the authenticated bot/user profile.
├── search <QUERY> [--stream STREAMS] [--all-streams] [--since-hours SINCE-HOURS] [--per-stream PER-STREAM] [--limit LIMIT] [--json-output]  # Search message content using stream-scoped Zulip narrows.
├── search-topics <QUERY> [--stream STREAMS] [--all-streams] [--limit LIMIT] [--json-output]  # Search topic names across explicitly selected public streams.
├── streams [--all] [--json-output]  # List streams, subscribed by default.
├── topic [--stream STREAM] [--topic TOPIC-NAME] [--batch-size BATCH-SIZE] [--max-requests MAX-REQUESTS] [--output OUTPUT] [--json-output] [--interactive]  # Export a full stream/topic thread.
└── topics [--stream STREAM] [--json-output] [--interactive]  # List topics for a stream.
```

Brief output:

```text
chatzulip
├── --help  # Show this message and exit.
├── --version  # Show the version and exit.
├── --tree  # Print the registered CLI tree and exit.
├── --tree-brief  # Print the registered CLI tree without parameter signatures and exit.
├── messages  # Fetch messages with optional Zulip narrow filters.
├── news  # Render recent Zulip updates to Markdown.
├── profile  # Show the authenticated bot/user profile.
├── search  # Search message content using stream-scoped Zulip narrows.
├── search-topics  # Search topic names across explicitly selected public streams.
├── streams  # List streams, subscribed by default.
├── topic  # Export a full stream/topic thread.
└── topics  # List topics for a stream.
```

`search-topics` and `search` require at least one repeatable `--stream`, or the explicit `--all-streams` switch. The latter may issue one API request per accessible public stream, so it is never an implicit default. Search results include canonical Zulip permalinks.

## Configuration

ChatZulip registers a typed ChatEnv `zulip` provider with these service-oriented fields:

```text
ZULIP_SITE
ZULIP_BOT_EMAIL
ZULIP_BOT_API_KEY
ZULIP_NEWS_STREAMS
ZULIP_NEWS_TOPICS
ZULIP_NEWS_SINCE_HOURS
ZULIP_NEWS_PER_STREAM
```

`ZULIP_BOT_API_KEY` is sensitive and must never be printed. Profiles are stored under `$CHATARCH_HOME/envs/Zulip/`.

## Python API mapping

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

`chatzulip news` uses the optional ChatTool LLM summarizer when available and falls back to a rule-based Markdown digest otherwise.

## Write boundary

The default CLI remains read-oriented. Write operations are importable Python and MCP capabilities:

- `chatzulip.operations.send_message()`
- `chatzulip.operations.react()`
- `chatzulip.operations.upload_file()`
- `chatzulip.mcp.register()`

Adding write commands to the CLI requires a separate design for confirmation, dry-run behavior, permissions, and real Zulip smoke tests.
