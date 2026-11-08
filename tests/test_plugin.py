"""Native plugins must point to shipped content and agree on release identity."""
from pathlib import Path
import json
import re

from edgex.coordination import ROLES


ROOT = Path(__file__).resolve().parents[1]


def test_plugin_manifests_resolve_and_versions_agree():
    project = (ROOT / "pyproject.toml").read_text()
    version = re.search(r'^version = "([^"]+)"', project, re.MULTILINE).group(1)
    for host in ("codex", "claude", "cursor"):
        data = json.loads((ROOT / f".{host}-plugin/plugin.json").read_text())
        assert data["name"] == "edgex"
        assert data["version"] == version
        paths = data["skills"] if isinstance(data["skills"], list) else [data["skills"]]
        for relative in paths:
            directory = ROOT / relative
            assert directory.is_dir()
            assert (directory / "edgex/SKILL.md").is_file()
            assert len(list(directory.glob("*/SKILL.md"))) == len(ROLES) + 1
    market = json.loads((ROOT / ".agents/plugins/marketplace.json").read_text())
    assert market["name"] == "edgex-agents"
    assert market["plugins"][0]["name"] == "edgex"
    assert (ROOT / market["plugins"][0]["source"]["path"]).resolve() == ROOT
    for host in ("claude", "cursor"):
        market = json.loads((ROOT / f".{host}-plugin/marketplace.json").read_text())
        assert market["name"] == "edgex-agents"
        assert market["plugins"][0]["name"] == "edgex"


def test_native_agents_load_their_specialist_skill():
    for role in ROLES:
        path = ROOT / f"agents/edgex-{role}.md"
        content = path.read_text()
        match = re.search(r"\[the specialist skill\]\(([^)]+)\)", content)
        assert match, path
        skill = (path.parent / match.group(1)).resolve()
        assert skill.is_relative_to(ROOT)
        assert skill.is_file()
        assert f"name: edgex-{role}\n" in skill.read_text()
