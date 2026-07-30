# test_zulip_operations

Code tests for `chatzulip.operations`, the reusable API layer shared by CLI and MCP adapters.

## Scope

- Zulip narrow construction
- stream name/id resolution
- topic Markdown rendering
- importable stream/topic/message/send/react/upload functions
- news Markdown generation and fallback summary

## Acceptance

- Operations are callable directly from Python without invoking Click.
- Fake clients can be injected for deterministic tests.
- `summarize_news()` writes Markdown and returns structured `NewsResult` metadata.
