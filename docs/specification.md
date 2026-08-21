# ChatZulip 规范

这个页面定义 `ChatZulip` 的第一版功能边界、目录结构、CLI/API 约定和发布 gate。它是 `ChatTool` 父包移除 PR 之前的独立包规范。

## 包身份

| 项 | 值 |
| --- | --- |
| PyPI distribution | `ChatZulip` |
| import module | `chatzulip` |
| CLI executable | `chatzulip` |
| GitHub repository | `ChatArch/ChatZulip` |
| 文档站 | `https://arch.gh.wzhecnu.cn/ChatZulip/` |
| 配置服务名 | `zulip` |
| 首个功能版本 | `0.1.0` |

## 配置边界

`ChatZulip` 配置建模的是外部服务 Zulip，而不是 Python 包本身，所以 ChatEnv provider 使用 `zulip`，字段保持 Zulip 服务语义：

```text
ZULIP_SITE
ZULIP_BOT_EMAIL
ZULIP_BOT_API_KEY
ZULIP_NEWS_STREAMS
ZULIP_NEWS_TOPICS
ZULIP_NEWS_SINCE_HOURS
ZULIP_NEWS_PER_STREAM
```

规则：

- `ZULIP_BOT_API_KEY` 必须标记为 sensitive，文档、测试、PR 评论和日志都不能打印真实值。
- 客户端构造时先读 ChatEnv active/profile 值，再允许显式参数覆盖。
- typed profile 统一存入 `$CHATARCH_HOME/envs/Zulip/`；显式选择 profile 时不得从进程环境回填缺失凭据。
- 包内不维护第二套 dotenv/profile 渲染逻辑；ChatEnv 是配置系统的唯一入口。
- 不引入 `CHATZULIP_*` 凭据别名，避免把服务凭据拆成包名命名空间。

## CLI 边界

第一版 CLI 只公开 read-oriented 和报告类命令：

```text
chatzulip streams                         # 列出已订阅 streams；--all 显示可访问 public streams
chatzulip topics --stream TEXT            # 列出 stream topics；缺 stream 时支持 ChatStyle 交互补问
chatzulip search-topics QUERY --stream TEXT # 在显式 stream 范围搜索 topic
chatzulip search QUERY --stream TEXT      # 在显式 stream 范围搜索消息
chatzulip topic --stream TEXT --topic TEXT # 导出完整 thread，可写 Markdown 文件
chatzulip messages [filters...]           # 按 stream/topic/sender/search 获取消息
chatzulip profile                         # 查看当前 bot/user profile
chatzulip news [filters...] --output PATH # 生成近期消息 Markdown 摘要
```

写操作暂不进入 CLI：

- `send_message`
- `react`
- `upload_file`

这些能力通过 importable Python API 和 MCP adapter 暴露。进入 CLI 前需要另一个小设计，明确确认、权限、dry-run 和真实 Zulip smoke gate。

## Python API 边界

代码分层：

```text
src/chatzulip/
├── client.py      # Zulip REST client；负责 HTTP、参数序列化、错误映射
├── config.py      # ChatEnv provider；只声明 Zulip 服务字段
├── operations.py  # 可复用业务/API 函数；CLI 和 MCP 共用
├── cli.py         # Click + ChatStyle 薄适配层
└── mcp.py         # FastMCP 工具注册适配层
```

约定：

- CLI 命令不得成为唯一业务入口；实质逻辑放在 `operations.py` 或 `client.py`。
- MCP adapter 只调用 `operations.py`，不重复实现 REST/格式化逻辑。
- `news` 的 LLM 摘要是可选能力：基础安装不依赖 `ChatTool`；安装 `chatzulip[llm]` 后才尝试复用 `chattool` summarizer，失败时降级为 rule-based 摘要。

## 测试结构

保留 ChatPyPI 0.2.4 模板的三类测试目录，并把新增测试放进对应区域：

```text
tests/
├── cli-tests/       # 真实服务/人工运行的 doc-first CLI 用例
├── mock-cli-tests/  # fake client / mock CLI 自动化测试
├── code-tests/      # client、operations、config 等代码测试
└── test_version.py  # 模板级版本 smoke
```

验证 gate：

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

## 发布与父包迁移顺序

1. 合并 `ChatZulip` 功能 PR。
2. 从合并后的 `main` 打 `v0.1.0` 标签，通过 PyPI Trusted Publisher 发布。
3. clean install 验证 `ChatZulip==0.1.0`。
4. 再从最新 `ChatTool` 默认分支开独立 PR，移除 `chattool zulip` 内置实现。
5. `ChatTool` 父包保留 aggregate extra，例如 `chattool[zulip] -> ChatZulip>=0.1.0,<0.2.0`，但 base install 不应再包含重复 Zulip 业务逻辑。

## 不做的事

- 不在本 PR 中改 `ChatTool`。
- 不把 Zulip 写操作直接做成默认 CLI 命令。
- 不把 Zulip 凭据改名为 `CHATZULIP_*`。
- 不手动上传功能版 PyPI；`0.1.0+` 必须走 tag-driven Trusted Publisher。
