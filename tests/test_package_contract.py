from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10 compatibility
    import tomli as tomllib


def _project_metadata() -> dict:
    return tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))["project"]


def test_console_script_and_chatarch_runtime_dependencies_are_bounded():
    project = _project_metadata()

    assert project["scripts"] == {"chatzulip": "chatzulip.cli:main"}
    assert "chatstyle>=0.2.0,<0.3.0" in project["dependencies"]
    assert "chatenv>=0.2.10,<0.3.0" in project["dependencies"]
    assert project["entry-points"]["chatenv.configs"] == {"zulip": "chatzulip.config"}


def test_ci_checks_supported_pythons_and_installed_cli_contract():
    workflow = Path(".github/workflows/ci.yml").read_text(encoding="utf-8")

    for version in ("3.10", "3.11", "3.12"):
        assert f'"{version}"' in workflow
    for command in (
        "python -m pytest -q",
        "chatzulip --version",
        "chatzulip --tree",
        "chatzulip --tree-brief",
        "python -m build",
        "python -m twine check dist/*",
        "mkdocs build --strict",
    ):
        assert command in workflow
