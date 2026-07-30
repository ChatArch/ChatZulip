# ChatZulip 文档

ChatZulip 是 ChatArch 的 Zulip 集成包。当前功能版把 `ChatTool` 里的 Zulip client、read-oriented CLI、Markdown news digest 和 MCP adapter 提取到独立包中，并保留后续 `ChatTool` 父包移除的清晰边界。

站点入口：<https://arch.gh.wzhecnu.cn/ChatZulip/>

## 按场景选择文档

| 场景 | 文档 |
| --- | --- |
| 了解包身份、配置边界、发布 gate 和父包迁移顺序 | [ChatZulip 规范](specification.md) |
| 第一次安装、运行 CLI、确认包可用 | [CLI 能力地图](cli-tree.md) |
| 从 Python 代码调用包能力 | [Python 接口树](interface-tree.md) |
| 记录已实现、已验证、未实现能力边界 | [开发计划](development-plan.md) |

## 当前能力摘要

- ChatEnv provider：`zulip`，字段使用 `ZULIP_*` 服务语义。
- CLI：`streams`、`topics`、`topic`、`messages`、`profile`、`news`。
- Python API：`ZulipClient` 和 `chatzulip.operations`。
- MCP adapter：`chatzulip.mcp.register()`。
- 写操作：先作为 Python/MCP 能力保留，暂不进入默认 CLI。

## 文档状态约定

- **已实现**：代码、测试或 CLI 路径已经存在。
- **已验证**：已经通过本地 smoke、CI 或真实服务实践验证。
- **未实现**：只写规划和安全边界，不写成可执行教程；实现并验证后再升级为操作文档。

## 本地预览

```bash
python -m pip install -e ".[docs]"
mkdocs serve
```

英文首页见站点语言入口：<https://arch.gh.wzhecnu.cn/ChatZulip/en/>。缺少英文翻译的专题页会按 i18n fallback 回退到中文页面。
