from pathlib import Path


def test_mkdocs_material_theme_has_material_icon_renderer():
    config = Path("mkdocs.yml").read_text(encoding="utf-8")

    assert "name: material" in config
    assert "pymdownx.emoji" in config
    assert "material.extensions.emoji.twemoji" in config
    assert "material.extensions.emoji.to_svg" in config
