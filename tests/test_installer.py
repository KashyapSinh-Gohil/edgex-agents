from __future__ import annotations

from hashlib import sha256
from importlib import resources
import json
from pathlib import Path
from zipfile import ZipFile

import pytest

from edgex import installer


@pytest.fixture
def package(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    package = tmp_path / "package"
    skill = package / "assets/skills/edgex-research"
    (skill / "references").mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: edgex-research\ndescription: Research carefully.\n---\n\n"
        "Read [the protocol](references/protocol.md).\n", encoding="utf-8"
    )
    (skill / "references/protocol.md").write_text("Check evidence.\n", encoding="utf-8")
    (skill / "references/data.bin").write_bytes(b"\x00\xff\r\n")
    monkeypatch.setattr(installer.resources, "files", lambda anchor: package)
    return package


def snapshot(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*") if path.is_file()
    }


@pytest.mark.parametrize("target,base", [
    ("codex", ".agents/skills"),
    ("claude", ".claude/skills"),
    ("cursor", ".cursor/skills"),
    ("copilot", ".github/skills"),
    ("generic", ".edgex/skills"),
])
def test_install_targets(package: Path, tmp_path: Path, target: str, base: str) -> None:
    project = tmp_path / "project"
    paths = installer.install_package(target, project)
    source = package / "assets/skills/edgex-research"
    for path in source.rglob("*"):
        if path.is_file():
            destination = project / base / "edgex-research" / path.relative_to(source)
            assert destination.read_bytes() == path.read_bytes()
            assert str(destination) in paths
    assert paths == sorted(paths)
    assert all(Path(path).is_absolute() and Path(path).is_file() for path in paths)
    manifest = json.loads((project / ".edgex/install-manifest.json").read_text())
    assert manifest["version"] == 1
    assert len(manifest["files"]) == len(paths) - 1
    for relative, digest in manifest["files"].items():
        assert sha256((project / relative).read_bytes()).hexdigest() == digest
    if target == "generic":
        assert ".edgex/skills/edgex-research/SKILL.md" in (project / "EDGE-X.md").read_text()


def test_claude_agent_resolves_skill_references(package: Path, tmp_path: Path) -> None:
    project = tmp_path / "project"
    installer.install_package("claude", project)
    agent = (project / ".claude/agents/edgex-research.md").read_text()
    assert agent.startswith("---\nname: edgex-research\ndescription:")
    assert ".claude/skills/edgex-research/SKILL.md" in agent
    assert "against `.claude/skills/edgex-research/`" in agent
    assert "[the protocol](../skills/edgex-research/references/protocol.md)" in agent
    assert (project / ".claude/agents/../skills/edgex-research/references/protocol.md").is_file()


def test_claude_uses_frontmatter_name(package: Path, tmp_path: Path) -> None:
    source = package / "assets/skills/edgex-research/SKILL.md"
    source.write_text('---\nname: "edgex-review"\n---\nReview.\n')
    project = tmp_path / "project"
    installer.install_package("claude", project)
    assert (project / ".claude/agents/edgex-review.md").is_file()
    assert not (project / ".claude/agents/edgex-research.md").exists()


def test_non_edgex_skill_has_no_native_agent(package: Path, tmp_path: Path) -> None:
    (package / "assets/skills/edgex-research/SKILL.md").write_text("---\nname: other-skill\n---\nBody.\n")
    project = tmp_path / "project"
    installer.install_package("claude", project)
    assert not (project / ".claude/agents").exists()


def test_all_is_union_and_keeps_prior_targets(package: Path, tmp_path: Path) -> None:
    project = tmp_path / "project"
    union: set[str] = set()
    for target in ("codex", "claude", "cursor", "copilot", "generic"):
        union.update(installer.install_package(target, project))
    before = snapshot(project)
    assert set(installer.install_package("all", project)) == union
    assert snapshot(project) == before


def test_repeat_is_no_op(package: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    project = tmp_path / "project"
    paths = installer.install_package("all", project)
    before = snapshot(project)
    def unexpected_write(*args: object) -> None:
        pytest.fail("Repeat installation must not rewrite files")
    monkeypatch.setattr(installer, "_atomic_write", unexpected_write)
    assert installer.install_package("all", project) == paths
    assert snapshot(project) == before


def test_dry_run_creates_nothing(package: Path, tmp_path: Path) -> None:
    project = tmp_path / "absent/parent/project"
    paths = installer.install_package("all", project, True)
    assert not project.parent.parent.exists()
    assert installer.install_package("all", project) == paths


@pytest.mark.parametrize("relative", [
    ".github/skills/edgex-research/references/protocol.md",
    ".claude/agents/edgex-research.md",
    "EDGE-X.md",
])
@pytest.mark.parametrize("dry_run", [False, True])
def test_conflicts_preflight_entire_plan(package: Path, tmp_path: Path, relative: str, dry_run: bool) -> None:
    project = tmp_path / "project"
    user_file = project / relative
    user_file.parent.mkdir(parents=True)
    user_file.write_text("User content\n")
    before = snapshot(project)
    directories = set(project.rglob("*"))
    with pytest.raises(installer.InstallConflictError, match="user file"):
        installer.install_package("all", project, dry_run)
    assert snapshot(project) == before
    assert set(project.rglob("*")) == directories


def test_preserves_unrelated_files_and_adopts_identical(package: Path, tmp_path: Path) -> None:
    project = tmp_path / "project"
    skill = project / ".agents/skills/edgex-research"
    skill.mkdir(parents=True)
    source = package / "assets/skills/edgex-research/SKILL.md"
    (skill / "SKILL.md").write_bytes(source.read_bytes())
    (skill / "personal.md").write_text("User notes\n")
    installer.install_package("codex", project)
    assert (skill / "personal.md").read_text() == "User notes\n"
    assert ".agents/skills/edgex-research/personal.md" not in json.loads(
        (project / ".edgex/install-manifest.json").read_text()
    )["files"]


def test_upgrade_and_deleted_file_repair(package: Path, tmp_path: Path) -> None:
    project = tmp_path / "project"
    installer.install_package("all", project)
    reference = package / "assets/skills/edgex-research/references/protocol.md"
    reference.write_text("Upgraded protocol\n")
    (project / ".agents/skills/edgex-research/SKILL.md").unlink()
    before = snapshot(project)
    installer.install_package("all", project, True)
    assert snapshot(project) == before
    installer.install_package("all", project)
    assert (project / ".agents/skills/edgex-research/SKILL.md").exists()
    assert (project / ".github/skills/edgex-research/references/protocol.md").read_text() == "Upgraded protocol\n"
    installer.install_package("all", project)


@pytest.mark.parametrize("relative", [
    ".agents/skills/edgex-research/SKILL.md",
    ".github/skills/edgex-research/references/protocol.md",
    ".claude/agents/edgex-research.md",
    "EDGE-X.md",
])
def test_edited_owned_file_blocks_upgrade(package: Path, tmp_path: Path, relative: str) -> None:
    project = tmp_path / "project"
    installer.install_package("all", project)
    (project / relative).write_text("Local edit\n")
    (package / "assets/skills/edgex-research/references/protocol.md").write_text("Upgrade\n")
    before = snapshot(project)
    with pytest.raises(installer.InstallConflictError, match="Locally edited"):
        installer.install_package("all", project)
    assert snapshot(project) == before


@pytest.mark.parametrize("relative", [
    ".agents", ".agents/skills", ".agents/skills/edgex-research",
    ".agents/skills/edgex-research/SKILL.md",
    ".agents/skills/edgex-research/references",
    ".edgex", ".edgex/install-manifest.json", "EDGE-X.md",
])
@pytest.mark.parametrize("dangling", [False, True])
def test_destination_symlinks_refused(package: Path, tmp_path: Path, relative: str, dangling: bool) -> None:
    project = tmp_path / "project"
    link = project / relative
    link.parent.mkdir(parents=True)
    outside = tmp_path / "outside"
    if not dangling:
        outside.mkdir()
        (outside / "keep.txt").write_text("Untouched\n")
    link.symlink_to(outside, target_is_directory=True)
    before = snapshot(outside) if outside.exists() else {}
    directories = set(project.rglob("*"))
    with pytest.raises(installer.InstallerError, match="symlink"):
        installer.install_package("all", project)
    assert set(project.rglob("*")) == directories
    assert (snapshot(outside) if outside.exists() else {}) == before
    assert link.is_symlink()


def test_project_symlink_refused(package: Path, tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.symlink_to(tmp_path / "absent", target_is_directory=True)
    with pytest.raises(installer.InstallerError, match="symlink project"):
        installer.install_package("codex", project)
    assert not (tmp_path / "absent").exists()


@pytest.mark.parametrize("relative", [
    "../escape.md", "/tmp/escape.md", ".agents/skills/../../escape.md",
    ".agents/skills/edgex-research/../escape.md", ".agents\\skills\\escape.md",
    "C:/escape.md", "unrelated.txt", ".edgex/install-manifest.json",
])
def test_manifest_traversal_refused(package: Path, tmp_path: Path, relative: str) -> None:
    project = tmp_path / "project"
    manifest = project / ".edgex/install-manifest.json"
    manifest.parent.mkdir(parents=True)
    manifest.write_text(json.dumps({"version": 1, "files": {relative: "0" * 64}}))
    before = snapshot(project)
    with pytest.raises(installer.InstallerError):
        installer.install_package("all", project)
    assert snapshot(project) == before


@pytest.mark.parametrize("content", ["user notes", "[]", '{"version":2,"files":{}}',
    '{"version":1,"files":[]}', '{"version":1,"files":{"EDGE-X.md":"bad"}}'])
def test_invalid_manifest_preserved(package: Path, tmp_path: Path, content: str) -> None:
    project = tmp_path / "project"
    manifest = project / ".edgex/install-manifest.json"
    manifest.parent.mkdir(parents=True)
    manifest.write_text(content)
    before = snapshot(project)
    with pytest.raises(installer.InstallerError):
        installer.install_package("codex", project)
    assert snapshot(project) == before


def test_file_in_directory_position_refused(package: Path, tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    (project / ".agents").write_text("User file\n")
    with pytest.raises(installer.InstallConflictError):
        installer.install_package("codex", project)
    assert snapshot(project) == {".agents": b"User file\n"}


def test_resource_symlink_refused(package: Path, tmp_path: Path) -> None:
    project = tmp_path / "project"
    (package / "assets/skills/edgex-research/references/leak.md").symlink_to(tmp_path / "outside")
    with pytest.raises(installer.InstallerError, match="resource symlink"):
        installer.install_package("codex", project)
    assert not project.exists()


def test_duplicate_agent_refused(package: Path, tmp_path: Path) -> None:
    skill = package / "assets/skills/edgex-other"
    skill.mkdir()
    (skill / "SKILL.md").write_text("---\nname: edgex-research\n---\nDuplicate agent\n")
    project = tmp_path / "project"
    with pytest.raises(installer.InstallerError, match="Duplicate destination"):
        installer.install_package("all", project)
    assert not project.exists()


@pytest.mark.parametrize("paths", [
    {".agents/skills/edgex-test/A.md", ".agents/skills/edgex-test/a.md"},
    {".agents/skills/edgex-test/Refs/a.md", ".agents/skills/edgex-test/refs/b.md"},
    {".agents/skills/edgex-test/ref", ".agents/skills/edgex-test/ref/a.md"},
])
def test_plan_collisions_refused(paths: set[str]) -> None:
    with pytest.raises(installer.InstallerError):
        installer._check_collisions(paths)


def test_atomic_replace_failure_keeps_original(package: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    project = tmp_path / "project"
    installer.install_package("codex", project)
    (package / "assets/skills/edgex-research/SKILL.md").write_text("New skill\n")
    before = snapshot(project)
    entries = set(project.rglob("*"))
    def replace_failure(source: str, destination: Path) -> None:
        raise OSError("Simulated replace failure")
    monkeypatch.setattr(installer.os, "replace", replace_failure)
    with pytest.raises(OSError, match="Simulated"):
        installer.install_package("codex", project)
    assert snapshot(project) == before
    assert set(project.rglob("*")) == entries


def test_resource_traversal_refused(package: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    class UnsafeChild:
        name = "../escape"

    class UnsafeSkills:
        def is_dir(self) -> bool:
            return True

        def iterdir(self) -> list[UnsafeChild]:
            return [UnsafeChild()]

    class UnsafePackage:
        def joinpath(self, name: str) -> UnsafePackage | UnsafeSkills:
            return UnsafeSkills() if name == "skills" else self

    monkeypatch.setattr(resources, "files", lambda anchor: UnsafePackage())
    project = tmp_path / "project"
    with pytest.raises(installer.InstallerError, match="Unsafe"):
        installer.install_package("all", project)
    assert not project.exists()


def test_zip_resources(package: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    archive = tmp_path / "package.zip"
    from zipfile import Path as ZipPath
    with ZipFile(archive, "w") as stream:
        for source in package.rglob("*"):
            if source.is_file():
                stream.write(source, source.relative_to(package).as_posix())
    with ZipFile(archive) as stream:
        monkeypatch.setattr(resources, "files", lambda anchor: ZipPath(stream))
        project = tmp_path / "project"
        installer.install_package("all", project)
        assert (project / ".agents/skills/edgex-research/references/data.bin").read_bytes() == b"\x00\xff\r\n"


def test_missing_resources_and_invalid_target(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(resources, "files", lambda anchor: tmp_path / "absent")
    project = tmp_path / "project"
    with pytest.raises(installer.InstallerError, match="no assets/skills"):
        installer.install_package("codex", project)
    with pytest.raises(installer.InstallerError, match="Unknown"):
        installer.install_package("bogus", project)
    assert not project.exists()
