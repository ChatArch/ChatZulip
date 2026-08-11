<div align="center">
    <a href="https://pypi.python.org/pypi/ChatZulip">
        <img src="https://img.shields.io/pypi/v/ChatZulip.svg" alt="PyPI version" />
    </a>
    <a href="https://github.com/ChatArch/ChatZulip/actions/workflows/ci.yml">
        <img src="https://github.com/ChatArch/ChatZulip/actions/workflows/ci.yml/badge.svg" alt="Tests" />
    </a>
    <a href="https://arch.gh.wzhecnu.cn/ChatZulip/">
        <img src="https://img.shields.io/badge/docs-mkdocs-blue.svg" alt="Documentation" />
    </a>
</div>

<div align="center">

[English](README.en.md) | [简体中文](README.md)
</div>

# ChatZulip

ChatZulip is the ChatArch Zulip integration package. It provides ChatEnv-backed Zulip configuration, a Zulip REST client, read-oriented CLI commands, Markdown news digests, and MCP adapters.

## Quick Start

```bash
pip install -e ".[dev]"
chatzulip --help
chatzulip --version
chatzulip --tree
python -m pytest -q

# Configure Zulip credentials with ChatEnv, then use the CLI.
chatenv test -t zulip -I
chatzulip streams
chatzulip topics --stream general
chatzulip search-topics conjecture --all-streams
chatzulip search comparator --stream lean4 --since-hours 168
chatzulip messages --stream general --before 5
chatzulip news --stream general --since-hours 24 --output zulip-news.md
```

For package boundaries, CLI/API conventions, and release order, see [ChatZulip Specification](docs/specification.en.md).

## CLI Contract

This package depends on `chatstyle>=0.1.0,<0.2.0`, `chatenv>=0.2.3,<0.3.0`, and `httpx>=0.28.1,<1.0`. New commands should prefer:

- `CommandSchema` / `CommandField` for inputs.
- `add_interactive_option()` for the shared `-i/-I` switch.
- `resolve_command_inputs()` for missing args, defaults, TTY behavior, and validation.
- Generate `config.py` and a `chatenv.configs` entry point by default so the package is ChatEnv-discoverable; use `--without-chatenv-provider` only when ChatEnv integration is intentionally not needed.

## Layout

- `src/`: package source code
- `tests/code-tests/`: client, operations, config, and other code tests
- `tests/cli-tests/`: doc-first real-service/manual CLI cases
- `tests/mock-cli-tests/`: fake-client/mock CLI automated tests
- `tests/test_version.py`: template-level version smoke
- `docs/`: long-lived project docs built by mkdocs

## Development Notes

See `DEVELOP.md` and `AGENTS.md` before expanding the scaffold.
