# test_chatzulip_cli_basic

Mock/fake client tests for the public `chatzulip` CLI. These tests do not require real Zulip credentials or network access.

## Scope

- `chatzulip --version`
- `chatzulip --tree`
- `chatzulip --tree-brief`
- `chatzulip streams`
- `chatzulip topics --stream ...`
- `chatzulip topics -I` missing-argument failure
- `chatzulip topic --stream ... --topic ...`
- `chatzulip messages --json-output`
- `chatzulip profile`
- `chatzulip news` rule-based fallback when optional LLM summarizer is unavailable

## Acceptance

- Every CLI command delegates to `chatzulip.operations` or `ZulipClient` through a fake client.
- Full and brief trees come from the registered Click surface, preserve command descriptions, and differ only in parameter signatures.
- Missing required input in non-interactive mode exits non-zero.
- News output writes Markdown and reports LLM fallback without failing the command.
