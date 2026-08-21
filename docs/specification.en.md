# ChatZulip Specification

This page defines the first functional `ChatZulip` boundary: package identity, code layout, CLI/API contract, tests, and release gates. It is the standalone package contract before the follow-up `ChatTool` parent-removal PR.

## Package Identity

| Item | Value |
| --- | --- |
| PyPI distribution | `ChatZulip` |
| import module | `chatzulip` |
| CLI executable | `chatzulip` |
| GitHub repository | `ChatArch/ChatZulip` |
| Documentation site | `https://arch.gh.wzhecnu.cn/ChatZulip/` |
| Configuration service name | `zulip` |
| First functional version | `0.1.0` |

## Configuration Boundary

`ChatZulip` models the external Zulip service, not the package name itself. The ChatEnv provider is therefore `zulip`, and fields keep Zulip service semantics:

```text
ZULIP_SITE
ZULIP_BOT_EMAIL
ZULIP_BOT_API_KEY
ZULIP_NEWS_STREAMS
ZULIP_NEWS_TOPICS
ZULIP_NEWS_SINCE_HOURS
ZULIP_NEWS_PER_STREAM
```

Rules:

- `ZULIP_BOT_API_KEY` is sensitive. Do not print real values in docs, tests, PR comments, or logs.
- Client construction loads ChatEnv active/profile values before explicit constructor overrides.
- Typed profiles live under `$CHATARCH_HOME/envs/Zulip/`; an explicitly selected profile must not backfill missing credentials from the process environment.
- The package must not maintain a second dotenv/profile renderer; ChatEnv is the configuration system.
- Do not add `CHATZULIP_*` credential aliases unless a future migration explicitly requires them.

## CLI Boundary

The first CLI version exposes read-oriented and reporting commands:

```text
chatzulip streams                          # List subscribed streams; --all shows accessible public streams
chatzulip topics --stream TEXT             # List stream topics; missing stream can use ChatStyle prompts
chatzulip search-topics QUERY --stream TEXT # Search topics in explicit stream scope
chatzulip search QUERY --stream TEXT       # Search messages in explicit stream scope
chatzulip topic --stream TEXT --topic TEXT # Export a full thread, optionally to Markdown
chatzulip messages [filters...]            # Fetch messages by stream/topic/sender/search
chatzulip profile                          # Show the authenticated bot/user profile
chatzulip news [filters...] --output PATH  # Render a Markdown news digest
```

Write operations are not CLI commands yet:

- `send_message`
- `react`
- `upload_file`

They are available through importable Python APIs and MCP adapters. CLI write commands need a separate design for confirmation, permissions, dry-run behavior, and real Zulip smoke tests.

## Python API Boundary

Code layout:

```text
src/chatzulip/
├── client.py      # Zulip REST client: HTTP, parameter serialization, error mapping
├── config.py      # ChatEnv provider: Zulip service fields only
├── operations.py  # Reusable business/API functions shared by CLI and MCP
├── cli.py         # Thin Click + ChatStyle adapter
└── mcp.py         # FastMCP registration adapter
```

Conventions:

- CLI commands must not be the only business entry point; core logic belongs in `operations.py` or `client.py`.
- The MCP adapter calls `operations.py` and does not duplicate REST or formatting logic.
- `news` LLM summarization is optional: the base install does not depend on `ChatTool`; `chatzulip[llm]` enables a best-effort `chattool` summarizer and falls back to a rule-based digest when unavailable.

## Test Structure

The repository keeps the ChatPyPI 0.2.4 test directory scaffold and places new tests by responsibility:

```text
tests/
├── cli-tests/       # Doc-first real-service/manual CLI cases
├── mock-cli-tests/  # Fake-client/mock CLI automated tests
├── code-tests/      # Client, operations, config code tests
└── test_version.py  # Template-level version smoke
```

Verification gates:

```bash
python -m pytest -q
chatzulip --version
chatzulip --tree
chatzulip --tree-brief
chatzulip --help
chatzulip topics -I
chatenv --home <task-local-home> test -t zulip -I
python -m build
python -m twine check dist/*
mkdocs build --strict
git diff --check
```

## Release And Parent Migration Order

1. Merge the `ChatZulip` feature PR.
2. Tag `v0.1.0` from merged `main` and publish through PyPI Trusted Publisher.
3. Clean-install verify `ChatZulip==0.1.0`.
4. Then create a separate `ChatTool` PR from the latest default branch to remove the bundled `chattool zulip` implementation.
5. Keep aggregate availability through an extra such as `chattool[zulip] -> ChatZulip>=0.1.0,<0.2.0`; base `ChatTool` should no longer ship duplicate Zulip business logic.

## Non-goals

- Do not modify `ChatTool` in this PR.
- Do not expose Zulip write operations as default CLI commands yet.
- Do not rename Zulip service credentials to `CHATZULIP_*`.
- Do not manually upload functional PyPI releases; `0.1.0+` must be tag-driven through Trusted Publisher.
