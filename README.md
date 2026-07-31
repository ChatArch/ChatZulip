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

ChatZulip 是 ChatArch 的 Zulip 集成包，提供 ChatEnv-backed Zulip 配置、Zulip REST client、read-oriented CLI、Markdown news digest 和 MCP adapter。

## 快速开始

```bash
pip install -e ".[dev]"
chatzulip --help
chatzulip --version
python -m pytest -q

# 先用 ChatEnv 配置 Zulip 凭据，再使用 CLI。
chatenv test -t zulip -I
chatzulip streams
chatzulip topics --stream general
chatzulip search-topics conjecture --all-streams
chatzulip search comparator --stream lean4 --since-hours 168
chatzulip messages --stream general --before 5
chatzulip news --stream general --since-hours 24 --output zulip-news.md
```

完整包边界、CLI/API 约定和发布顺序见文档页：[ChatZulip 规范](docs/specification.md)。

## CLI 规范

这个包依赖 `chatstyle>=0.1.0,<0.2.0`、`chatenv>=0.2.3,<0.3.0` 和 `httpx>=0.28.1,<1.0`，新的命令应优先使用：

- `CommandSchema` / `CommandField` 描述输入。
- `add_interactive_option()` 提供统一 `-i/-I`。
- `resolve_command_inputs()` 统一缺参补问、默认值、TTY 与校验。
- 默认生成 `config.py` 和 `chatenv.configs` entry point，使包可被 ChatEnv 发现；只有明确不需要 ChatEnv 接入时才使用 `--without-chatenv-provider`。

## 目录结构

- `src/`：包源码
- `tests/code-tests/`：client、operations、config 等代码测试
- `tests/cli-tests/`：真实服务/人工运行的 doc-first CLI 用例
- `tests/mock-cli-tests/`：fake client / mock CLI 自动化测试
- `tests/test_version.py`：模板级版本 smoke
- `docs/`：长期维护文档，由 mkdocs 构建

## 开发说明

扩展脚手架前，先阅读 `DEVELOP.md` 和 `AGENTS.md`。
