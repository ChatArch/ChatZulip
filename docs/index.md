# ChatZulip 文档

ChatZulip 是 ChatArch 系列 Python 包。这个文档站提供长期维护的使用说明、CLI/API 入口、能力地图和路线图。生成模板后，请把占位说明替换为当前包已经实现、探索过或计划中的真实内容。

站点入口：<https://arch.gh.wzhecnu.cn/ChatZulip/>

## 按场景选择文档

| 场景 | 文档 |
| --- | --- |
| 第一次安装、运行 CLI、确认包可用 | [CLI 能力地图](cli-tree.md) |
| 从 Python 代码调用包能力 | [Python 接口树](interface-tree.md) |
| 记录已实现、已验证、未实现能力边界 | [开发计划](development-plan.md) |

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
