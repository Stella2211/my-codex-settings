#!/usr/bin/env python3
"""Install the checked-in portion of a Codex configuration safely."""

from __future__ import annotations

import argparse
import copy
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from tomlkit import TOMLDocument, dumps, load, table
from tomlkit.items import Item, Table, InlineTable


BEGIN_MARKER = "<!-- BEGIN CODEX SETTINGS MANAGED BLOCK -->"
END_MARKER = "<!-- END CODEX SETTINGS MANAGED BLOCK -->"
BACKUP_DIR_NAME = ".codex-settings-backups"

# This is deliberately explicit: adding an arbitrary key to the checked-in
# file must not silently take over a user's local Codex configuration.
ALLOWED_KEYS = {
    "model",
    "model_reasoning_effort",
    "sandbox_mode",
    "approval_policy",
    "approvals_reviewer",
    "service_tier",
    "features",
    "memories",
    "mcp_servers",
}
ALLOWED_MCP_SERVERS = {"agent-browser", "freee_mcp"}
WINDOWS_CONFIG_OVERRIDES = {
    "approval_policy": "on-request",
    "approvals_reviewer": "auto_review",
    "sandbox_mode": "danger-full-access",
}


class InstallerError(RuntimeError):
    pass


def is_windows() -> bool:
    return os.name == "nt"


def source_dir() -> Path:
    return Path(__file__).resolve().parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--codex-home",
        type=Path,
        help="installation target (default: $CODEX_HOME or ~/.codex)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="validate and describe changes without writing or installing anything",
    )
    parser.add_argument(
        "--skip-agent-browser",
        action="store_true",
        help="skip the global agent-browser installation",
    )
    return parser.parse_args()


def target_dir(argument: Path | None) -> Path:
    if argument is not None:
        return argument.expanduser().resolve()
    return Path(os.environ.get("CODEX_HOME", "~/.codex")).expanduser().resolve()


def read_source(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise InstallerError(f"cannot read {path.name}: {exc}") from exc


def validate_source(config_path: Path) -> TOMLDocument:
    try:
        with config_path.open("rb") as stream:
            document = load(stream)
    except Exception as exc:
        raise InstallerError(f"cannot parse {config_path.name}: {exc}") from exc

    unexpected = set(document) - ALLOWED_KEYS
    if unexpected:
        names = ", ".join(sorted(unexpected))
        raise InstallerError(f"config.toml contains non-allowlisted keys: {names}")
    mcp_servers = document.get("mcp_servers")
    if mcp_servers is not None:
        unexpected_servers = set(mcp_servers) - ALLOWED_MCP_SERVERS
        if unexpected_servers:
            names = ", ".join(sorted(unexpected_servers))
            raise InstallerError(f"config.toml contains non-allowlisted MCP servers: {names}")
    return document


def clone_item(value: Item) -> Item:
    return copy.deepcopy(value)


def merge_table(destination: Table, source: Table) -> None:
    for key, source_value in source.items():
        if key not in destination:
            destination[key] = clone_item(source_value)
            continue

        destination_value = destination[key]
        if isinstance(source_value, (Table, InlineTable)):
            if isinstance(destination_value, bool):
                replacement = table()
                replacement.add("enabled", destination_value)
                destination[key] = replacement
                destination_value = replacement
            if isinstance(destination_value, (Table, InlineTable)):
                merge_table(destination_value, source_value)
            else:
                destination[key] = clone_item(source_value)
        else:
            destination[key] = clone_item(source_value)


def merged_config(source: TOMLDocument, existing: TOMLDocument | None) -> TOMLDocument:
    result = existing if existing is not None else TOMLDocument()
    merge_table(result, source)
    return result


def load_existing_config(path: Path) -> TOMLDocument | None:
    if not path.exists():
        return None
    try:
        with path.open("rb") as stream:
            return load(stream)
    except Exception as exc:
        raise InstallerError(f"cannot parse existing config.toml: {exc}") from exc


def atomic_write(path: Path, data: str, mode: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        # Windows does not expose fchmod.  chmod after replacement is best
        # effort there, while POSIX retains the restrictive temporary mode.
        fchmod = getattr(os, "fchmod", None)
        if fchmod is not None:
            fchmod(fd, mode)
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        os.chmod(path, mode)
    except Exception:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def backup_existing(paths: list[Path], target: Path, dry_run: bool) -> Path | None:
    existing = [path for path in paths if path.exists()]
    if not existing or dry_run:
        return None
    root = target / BACKUP_DIR_NAME
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    backup = root / timestamp
    suffix = 0
    while backup.exists():
        suffix += 1
        backup = root / f"{timestamp}-{suffix}"
    backup.mkdir(parents=True, mode=0o700)
    for path in existing:
        shutil.copy2(path, backup / path.name)
    return backup


def update_agents(existing: str | None, source: str) -> str:
    block = f"{BEGIN_MARKER}\n{source.rstrip()}\n{END_MARKER}\n"
    if existing is None:
        return block
    begin_count = existing.count(BEGIN_MARKER)
    end_count = existing.count(END_MARKER)
    if begin_count != end_count or begin_count > 1:
        raise InstallerError("existing AGENTS.md has malformed managed markers")
    if begin_count == 0:
        return existing.rstrip() + "\n\n" + block
    begin = existing.index(BEGIN_MARKER)
    end_start = existing.index(END_MARKER)
    if end_start < begin:
        raise InstallerError("existing AGENTS.md has reversed managed markers")
    end = end_start + len(END_MARKER)
    return existing[:begin] + block.rstrip() + existing[end:]


def run_agent_browser_install() -> str:
    if shutil.which("bun") is None:
        raise InstallerError("bun is required for agent-browser; install bun or use --skip-agent-browser")
    try:
        subprocess.run(["bun", "add", "--global", "agent-browser"], check=True, shell=is_windows())
        resolved = shutil.which("agent-browser")
        if resolved is None:
            raise InstallerError("agent-browser was installed but is not on PATH; add Bun's global bin directory to PATH")
        subprocess.run([resolved, "install"], check=True, shell=is_windows())
    except subprocess.CalledProcessError as exc:
        raise InstallerError(f"agent-browser installation failed (exit {exc.returncode})") from exc
    resolved = shutil.which("agent-browser")
    if resolved is None:
        raise InstallerError("agent-browser installation completed but its command was not found")
    return resolved


def install(args: argparse.Namespace) -> int:
    source = source_dir()
    required = [source / "config.toml", source / "AGENTS.md", source / "model-instructions-long-waits.md"]
    missing = [path.name for path in required if not path.is_file()]
    if missing:
        raise InstallerError(f"missing source file(s): {', '.join(missing)}")

    source_config = validate_source(required[0])
    home = target_dir(args.codex_home)
    config_path = home / "config.toml"
    agents_path = home / "AGENTS.md"
    model_path = home / "model-instructions-long-waits.md"

    # Validate local files and compute the merge before installing dependencies.
    existing_config = load_existing_config(config_path)
    existing_agents = agents_path.read_text(encoding="utf-8") if agents_path.exists() else None
    agents = update_agents(existing_agents, read_source(required[1]))
    model = read_source(required[2])
    config = merged_config(source_config, existing_config)
    if is_windows():
        for key, value in WINDOWS_CONFIG_OVERRIDES.items():
            config[key] = value
    config["model_instructions_file"] = str(model_path)

    if args.dry_run:
        print(f"dry-run: validated merge into {home}")
        if not args.skip_agent_browser:
            print("dry-run: would run bun add --global agent-browser and agent-browser install")
        if (home / "AGENTS.override.md").exists():
            print("warning: AGENTS.override.md exists and may supersede AGENTS.md")
        print("dry-run: no target files changed")
        return 0

    agent_command = None if args.skip_agent_browser else run_agent_browser_install()
    if agent_command is not None:
        config["mcp_servers"]["agent-browser"]["command"] = agent_command

    backup = backup_existing([config_path, agents_path, model_path], home, False)
    try:
        atomic_write(config_path, dumps(config), 0o600)
        atomic_write(agents_path, agents, 0o644)
        atomic_write(model_path, model, 0o644)
    except Exception as exc:
        raise InstallerError(f"installation failed after backup {backup}: {exc}") from exc
    print(f"installed Codex settings into {home}")
    override_path = home / "AGENTS.override.md"
    if override_path.exists():
        print(f"warning: existing {override_path} was left unchanged; review its precedence")
    if backup:
        print(f"backup created at {backup}")
    return 0


def main() -> int:
    try:
        return install(parse_args())
    except InstallerError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
