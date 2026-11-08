"""Validate distributable instructions as data, including installed-wheel runs."""
from importlib.resources import files
import re

from edgex.coordination import ROLES


def test_complete_skill_bundle_and_local_references():
    root = files("edgex").joinpath("assets", "skills")
    for name in ["edgex", *(f"edgex-{role}" for role in ROLES)]:
        skill = root.joinpath(name, "SKILL.md")
        text = skill.read_text(encoding="utf-8")
        assert text.startswith("---\n")
        assert f"name: {name}\n" in text
        assert re.search(r"^description:\s*\S", text, re.MULTILINE)
        for ref in re.findall(r"\]\((references/[^)#]+)(?:#[^)]*)?\)", text):
            assert root.joinpath(name, ref).is_file(), (name, ref)
        assert root.joinpath(name, "references", "protocol.md").is_file()
