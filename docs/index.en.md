# ChatZulip Docs

ChatZulip is a ChatArch Python package. This documentation site should hold long-lived usage notes, CLI/API entry points, capability maps, and roadmap notes. After scaffolding, replace placeholders with behavior that is actually implemented, explored, or planned for this package.

## Choose By Scenario

| Scenario | Document |
| --- | --- |
| Install the package, run the CLI, and confirm it works | [CLI Capability Map](cli-tree.md) |
| Call package behavior directly from Python | [Python Interface Tree](interface-tree.md) |
| Record implemented, verified, and planned capability boundaries | [Development Plan](development-plan.md) |

## Documentation Status

- **Implemented**: code, tests, or CLI routes exist.
- **Verified**: covered by local smoke, CI, or real-service practice.
- **Not implemented**: keep as roadmap and safety notes only; turn into operation docs after implementation and validation.

## Local Preview

```bash
python -m pip install -e ".[docs]"
mkdocs serve
```

The Chinese home page is available at <https://arch.gh.wzhecnu.cn/ChatZulip/>. Topic pages without English translations fall back to the default Chinese content through the i18n plugin.
