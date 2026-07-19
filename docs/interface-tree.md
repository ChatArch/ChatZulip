# Python 接口树

`ChatZulip` 的 CLI 保持薄入口；实质能力放在可 import 的 Python 函数和类中，便于其他 ChatArch 包、MCP adapter 或自动化脚本直接调用。

## 包入口

```python
from chatzulip import ZulipClient, ZulipConfig, __version__
```

## 核心模块

```text
chatzulip
├── client.py      # Zulip REST client
├── config.py      # ChatEnv Zulip provider schema
├── operations.py  # CLI/MCP 背后的 importable operations
├── cli.py         # Click CLI thin adapter
└── mcp.py         # FastMCP registration adapter
```

## 常用 API

```python
from chatzulip.client import ZulipClient
from chatzulip import operations

client = ZulipClient()
streams = operations.list_streams(client)
messages = operations.get_messages(stream="general", topic="release", client=client)
markdown = operations.render_topic_markdown("general", "release", messages)
```

## 写操作 API

```python
operations.send_message(to="general", content="hello", topic="release")
operations.react(message_id=123, emoji_name="thumbs_up")
operations.upload_file("/path/to/file.txt")
```

这些写操作目前不作为默认 CLI 命令暴露；如果进入 CLI，需要单独增加确认/权限/真实服务测试。
