"""Project-scoped installation of the skill bundles shipped in the wheel.

The manifest records SHA-256 hashes, not permission to overwrite local edits.
All conflicts are checked before creating directories or writing files. Each
changed file is replaced atomically; the manifest is committed last. This is
not a transaction across files in the event of an I/O failure.
"""

from __future__ import annotations

from hashlib import sha256
from importlib import resources
from importlib.resources.abc import Traversable
import json
import os
from pathlib import Path, PurePosixPath
import re
import tempfile


_DESTINATIONS = {
    "codex": ".agents/skills",
    "claude": ".claude/skills",
    "cursor": ".cursor/skills",
    "copilot": ".github/skills",
    "generic": ".edgex/skills",
}
_MANIFEST = ".edgex/install-manifest.json"
_HASH = re.compile(r"[0-9a-f]{64}\Z")
_AGENT_NAME = re.compile(r"edgex-[a-z0-9]+(?:-[a-z0-9]+)*\Z")


class InstallerError(ValueError):
    """An unsafe path, invalid bundle, or invalid manifest prevents installation."""


class InstallConflictError(InstallerError):
    """Installation would overwrite an unowned file or a locally edited file."""


def _parts(relative: str) -> tuple[str, ...]:
    """Accept only canonical relative paths that are portable to Windows."""
    path = PurePosixPath(relative)
    parts = path.parts
    if (
        not parts
        or path.is_absolute()
        or path.as_posix() != relative
        or any(part in {".", ".."} for part in parts)
        or any(
            any(ord(char) < 32 or char in '\\:<>"|?*' for char in part)
            or part.endswith((".", " "))
            or part.split(".", 1)[0].upper()
            in {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)),
                *(f"LPT{i}" for i in range(1, 10))}
            for part in parts
        )
    ):
        raise InstallerError(f"Unsafe installation path: {relative!r}")
    return parts


def _destination(root: Path, relative: str) -> Path:
    parts = _parts(relative)
    if root.is_symlink():
        raise InstallerError(f"Refusing symlink project: {root}")
    if root.exists() and not root.is_dir():
        raise InstallConflictError(f"Expected a project directory: {root}")
    current = root
    for index, part in enumerate(parts):
        current = current / part
        if current.is_symlink():
            raise InstallerError(f"Refusing symlink: {current}")
        if current.exists():
            if index < len(parts) - 1 and not current.is_dir():
                raise InstallConflictError(f"Expected a directory: {current}")
            if index == len(parts) - 1 and not current.is_file():
                raise InstallConflictError(f"Expected a regular file: {current}")
    return current


def _read(root: Path, relative: str) -> bytes | None:
    path = _destination(root, relative)
    return path.read_bytes() if path.exists() else None


def _resource_symlink(resource: Traversable) -> None:
    # Filesystem resources expose symlinks; zip resources have no symlink API.
    if isinstance(resource, Path) and resource.is_symlink():
        raise InstallerError(f"Refusing package resource symlink: {resource}")


def _bundles() -> dict[str, dict[str, bytes]]:
    assets = resources.files("edgex").joinpath("assets")
    _resource_symlink(assets)
    skills = assets.joinpath("skills")
    _resource_symlink(skills)
    if not skills.is_dir():
        raise InstallerError("Package contains no assets/skills directory")
    bundles: dict[str, dict[str, bytes]] = {}

    def collect(directory: Traversable, prefix: str = "") -> dict[str, bytes]:
        files: dict[str, bytes] = {}
        for child in sorted(directory.iterdir(), key=lambda entry: entry.name):
            if len(_parts(child.name)) != 1:
                raise InstallerError(f"Unsafe resource name: {child.name!r}")
            _resource_symlink(child)
            relative = f"{prefix}{child.name}"
            if child.is_dir():
                files.update(collect(child, f"{relative}/"))
            elif child.is_file():
                files[relative] = child.read_bytes()
            else:
                raise InstallerError(f"Unsupported package resource: {relative}")
        return files

    for skill in sorted(skills.iterdir(), key=lambda entry: entry.name):
        if len(_parts(skill.name)) != 1:
            raise InstallerError(f"Unsafe skill name: {skill.name!r}")
        _resource_symlink(skill)
        if not skill.is_dir():
            continue
        bundle = collect(skill)
        if "SKILL.md" not in bundle:
            raise InstallerError(f"Skill {skill.name!r} has no SKILL.md")
        bundles[skill.name] = bundle
    if not bundles:
        raise InstallerError("Package contains no skill bundles")
    return bundles


def _agent(skill: str, content: bytes) -> tuple[str, bytes] | None:
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise InstallerError(f"Skill {skill!r} is not UTF-8") from exc
    lines = text.splitlines()
    name = skill
    body = text
    if lines and lines[0] == "---":
        try:
            end = lines.index("---", 1)
        except ValueError as exc:
            raise InstallerError(f"Unclosed frontmatter in skill {skill!r}") from exc
        for line in lines[1:end]:
            if line.startswith("name:"):
                name = line.partition(":")[2].strip()
                if name.startswith('"'):
                    try:
                        name = json.loads(name)
                    except json.JSONDecodeError as exc:
                        raise InstallerError(f"Invalid skill name in {skill!r}") from exc
                elif name.startswith("'") and name.endswith("'"):
                    name = name[1:-1].replace("''", "'")
                if not isinstance(name, str) or len(_parts(name)) != 1:
                    raise InstallerError(f"Invalid skill name in {skill!r}")
        body = "\n".join(lines[end + 1:]).lstrip("\n")
    if not _AGENT_NAME.fullmatch(name):
        if name.startswith("edgex-"):
            raise InstallerError(f"Invalid Claude agent name: {name!r}")
        return None
    skill_path = f".claude/skills/{skill}"
    # Rebase reference paths in the copied prompt, including Markdown links
    # and inline code paths. The canonical skill keeps its original paths.
    body = re.sub(
        r"(?<![\w./:\\-])(?:\./)?references/",
        lambda match: f"../skills/{skill}/references/",
        body,
    )
    agent = (
        f"---\nname: {name}\n"
        f"description: {json.dumps(f'EdgeX {name} agent; follow its bundled skill and references.')}\n"
        "---\n\n"
        f"Skill directory (relative to the project root): `{skill_path}/`.\n"
        f"Canonical skill: [SKILL.md](../skills/{skill}/SKILL.md).\n"
        f"Read `{skill_path}/SKILL.md` as the authoritative instructions. "
        f"Resolve every relative reference in those instructions against `{skill_path}/`, "
        "including `references/`; do not resolve them against `.claude/agents/`. "
        "Reference paths in the copied instructions below are relative to this agent file.\n\n"
        f"{body.rstrip()}\n"
    )
    return f".claude/agents/{name}.md", agent.encode("utf-8")


def _managed_path(relative: str) -> bool:
    parts = _parts(relative)
    if relative == "EDGE-X.md":
        return True
    if len(parts) == 3 and parts[:2] == (".claude", "agents"):
        return parts[2].endswith(".md") and bool(_AGENT_NAME.fullmatch(parts[2][:-3]))
    return any(
        len(parts) >= 4 and parts[:2] == tuple(base.split("/"))
        for base in _DESTINATIONS.values()
    )


def _manifest(content: bytes | None) -> dict[str, str]:
    if content is None:
        return {}
    try:
        data = json.loads(content)
    except (ValueError, UnicodeDecodeError) as exc:
        raise InstallerError("Invalid EdgeX install manifest") from exc
    if (
        not isinstance(data, dict)
        or set(data) != {"version", "files"}
        or type(data["version"]) is not int
        or data["version"] != 1
        or not isinstance(data["files"], dict)
    ):
        raise InstallerError("Unsupported EdgeX install manifest")
    for relative, digest in data["files"].items():
        if (
            not _managed_path(relative)
            or not isinstance(digest, str)
            or not _HASH.fullmatch(digest)
        ):
            raise InstallerError(f"Invalid manifest entry: {relative!r}")
    return data["files"]


def _check_collisions(paths: set[str]) -> None:
    # Reject aliases even on case-sensitive hosts so plans remain portable.
    seen: dict[str, str] = {}
    files = {path.casefold() for path in paths}
    for relative in sorted(paths):
        parts = _parts(relative)
        for index in range(1, len(parts) + 1):
            prefix = "/".join(parts[:index])
            folded = prefix.casefold()
            if folded in seen and seen[folded] != prefix:
                raise InstallerError(f"Case-colliding paths: {seen[folded]!r}, {prefix!r}")
            seen[folded] = prefix
            if index < len(parts) and folded in files:
                raise InstallerError(f"File/directory conflict: {prefix!r}")


def _atomic_write(root: Path, relative: str, content: bytes) -> None:
    path = _destination(root, relative)
    path.parent.mkdir(parents=True, exist_ok=True)
    _destination(root, relative)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        _destination(root, relative)
        os.replace(temporary, path)
    finally:
        if os.path.lexists(temporary):
            os.unlink(temporary)


def install_package(target: str, project: Path, dry_run: bool = False) -> list[str]:
    """Install bundled skills into a project, returning sorted absolute file paths.

    Targets: codex, claude, cursor, copilot, generic, or all (their union).
    Returned paths include the manifest and unchanged selected files. Dry runs
    return the same paths and perform the full preflight without any mutation.
    Existing identical unowned files may be adopted. Different unowned files,
    edited owned files, symlinks, and unsafe manifests raise InstallerError;
    ordinary filesystem failures propagate as OSError. No files are deleted.
    """
    if target != "all" and target not in _DESTINATIONS:
        raise InstallerError(f"Unknown installation target: {target!r}")
    project = Path(project).expanduser()
    if project.is_symlink():
        raise InstallerError(f"Refusing symlink project: {project}")
    root = project.resolve()
    for ancestor in (root, *root.parents):
        if ancestor.exists() and not ancestor.is_dir():
            raise InstallConflictError(f"Expected a project directory: {ancestor}")

    old_manifest = _read(root, _MANIFEST)
    owned = _manifest(old_manifest)
    bundles = _bundles()
    selected = tuple(_DESTINATIONS) if target == "all" else (target,)
    planned: dict[str, bytes] = {}

    def add(relative: str, content: bytes) -> None:
        if relative in planned:
            raise InstallerError(f"Duplicate destination: {relative}")
        planned[relative] = content

    for selected_target in selected:
        base = _DESTINATIONS[selected_target]
        for skill, bundle in bundles.items():
            for relative, content in bundle.items():
                add(f"{base}/{skill}/{relative}", content)
            if selected_target == "claude":
                agent = _agent(skill, bundle["SKILL.md"])
                if agent is not None:
                    add(*agent)
        if selected_target == "generic":
            entries = "\n".join(
                f"- [{skill}](.edgex/skills/{skill}/SKILL.md)" for skill in bundles
            )
            add("EDGE-X.md", (
                "# EdgeX\n\nFollow the applicable bundled skill instructions below. "
                "Resolve references relative to each skill's directory.\n\n"
                f"{entries}\n"
            ).encode("utf-8"))

    _check_collisions(set(planned) | set(owned) | {_MANIFEST})
    existing = {relative: _read(root, relative) for relative in sorted(set(planned) | set(owned))}
    for relative, digest in owned.items():
        current = existing[relative]
        if current is not None and sha256(current).hexdigest() != digest:
            raise InstallConflictError(f"Locally edited installed file: {root / relative}")
    for relative, content in planned.items():
        current = existing[relative]
        if relative not in owned and current is not None and current != content:
            raise InstallConflictError(f"Refusing to overwrite user file: {root / relative}")

    hashes = dict(owned)
    hashes.update({relative: sha256(content).hexdigest() for relative, content in planned.items()})
    manifest_content = (json.dumps({"version": 1, "files": hashes}, indent=2, sort_keys=True) + "\n").encode("utf-8")
    paths = sorted([*planned, _MANIFEST])
    if not dry_run:
        for relative in sorted(planned):
            if existing[relative] != planned[relative]:
                _atomic_write(root, relative, planned[relative])
        if old_manifest != manifest_content:
            _atomic_write(root, _MANIFEST, manifest_content)
    return [str(root / relative) for relative in paths]
