from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from .config import settings
from .models import FileChange


IGNORED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
    "dist",
    "build",
    ".next",
}

TEXT_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".json",
    ".md",
    ".txt",
    ".html",
    ".css",
    ".scss",
    ".yaml",
    ".yml",
    ".toml",
    ".ini",
    ".cfg",
    ".sql",
    ".sh",
}

SAFE_COMMAND_PATTERNS = [
    re.compile(r"^python(?:3)?\s+-m\s+pytest(?:\s+.*)?$"),
    re.compile(r"^pytest(?:\s+.*)?$"),
    re.compile(r"^python(?:3)?\s+-m\s+compileall(?:\s+.*)?$"),
    re.compile(r"^python(?:3)?\s+-m\s+unittest(?:\s+.*)?$"),
]


def _safe_path(relative_path: str) -> Path:
    """
    Resolve a path inside the CodeForge workspace.

    Prevents path traversal such as:
    ../../some-secret-file
    """

    relative_path = relative_path.replace("\\", "/").lstrip("/")

    candidate = (
        settings.workspace_dir / relative_path
    ).resolve()

    root = settings.workspace_dir.resolve()

    if candidate != root and root not in candidate.parents:
        raise ValueError(
            f"Unsafe path rejected: {relative_path}"
        )

    return candidate


def snapshot_workspace() -> str:
    """
    Read text files inside the workspace and return them
    as a single snapshot for the AI model.
    """

    root = settings.workspace_dir

    chunks: list[str] = []
    count = 0

    for path in sorted(root.rglob("*")):

        if count >= settings.max_workspace_files:
            chunks.append(
                "\n[Workspace truncated: file limit reached]\n"
            )
            break

        if not path.is_file():
            continue

        if any(
            part in IGNORED_DIRS
            for part in path.parts
        ):
            continue

        if (
            path.suffix.lower() not in TEXT_EXTENSIONS
            and path.name not in {"Dockerfile", "Makefile"}
        ):
            continue

        relative_path = path.relative_to(root).as_posix()

        try:
            content = path.read_text(
                encoding="utf-8"
            )
        except UnicodeDecodeError:
            continue

        if len(content) > settings.max_file_chars:
            content = (
                content[: settings.max_file_chars]
                + "\n...[truncated]"
            )

        chunks.append(
            f"\n--- FILE: {relative_path} ---\n"
            f"{content}\n"
        )

        count += 1

    if not chunks:
        return "[Workspace is empty.]"

    return "".join(chunks)


def apply_changes(
    changes: list[FileChange],
) -> list[str]:
    """
    Apply AI-generated file changes inside the workspace.
    """

    changed_files: list[str] = []

    for change in changes:

        target = _safe_path(change.path)

        if change.action == "delete":

            if target.is_file():
                target.unlink()

                changed_files.append(
                    f"deleted:{change.path}"
                )

            elif target.is_dir():
                shutil.rmtree(target)

                changed_files.append(
                    f"deleted:{change.path}"
                )

            continue

        if change.content is None:
            raise ValueError(
                f"Missing content for "
                f"{change.action}: {change.path}"
            )

        target.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        target.write_text(
            change.content,
            encoding="utf-8",
        )

        if change.action == "create":
            changed_files.append(
                f"created:{change.path}"
            )

        elif change.action == "update":
            changed_files.append(
                f"updated:{change.path}"
            )

        else:
            changed_files.append(
                f"{change.action}:{change.path}"
            )

    return changed_files


def _is_safe_command(command: str) -> bool:
    """
    Only allow a small number of safe validation commands.
    """

    normalized = " ".join(
        command.strip().split()
    )

    return any(
        pattern.fullmatch(normalized)
        for pattern in SAFE_COMMAND_PATTERNS
    )


def _convert_command_to_args(
    command: str,
) -> list[str] | None:
    """
    Convert the model-generated validation command
    into an argument list using the SAME Python executable
    currently running CodeForge.

    This ensures tests run inside the project's .venv.
    """

    parts = command.split()

    if command.startswith("python -m pytest"):
        return [
            sys.executable,
            "-m",
            "pytest",
            *parts[3:],
        ]

    if command.startswith("python3 -m pytest"):
        return [
            sys.executable,
            "-m",
            "pytest",
            *parts[3:],
        ]

    if command.startswith("pytest"):
        return [
            sys.executable,
            "-m",
            "pytest",
            *parts[1:],
        ]

    if command.startswith(
        "python -m compileall"
    ):
        return [
            sys.executable,
            "-m",
            "compileall",
            *parts[3:],
        ]

    if command.startswith(
        "python3 -m compileall"
    ):
        return [
            sys.executable,
            "-m",
            "compileall",
            *parts[3:],
        ]

    if command.startswith(
        "python -m unittest"
    ):
        return [
            sys.executable,
            "-m",
            "unittest",
            *parts[3:],
        ]

    if command.startswith(
        "python3 -m unittest"
    ):
        return [
            sys.executable,
            "-m",
            "unittest",
            *parts[3:],
        ]

    return None


def run_validation(
    commands: list[str],
) -> tuple[bool, str]:
    """
    Run validation commands inside the workspace.

    CodeForge uses sys.executable so that validation
    always runs with the same virtual environment as
    the FastAPI application.
    """

    if not commands:
        commands = [
            "python -m pytest"
        ]

    outputs: list[str] = []

    all_ok = True

    for command in commands[:4]:

        command = " ".join(
            command.strip().split()
        )

        if not _is_safe_command(command):

            outputs.append(
                f"$ {command}\n"
                "SKIPPED: command is not in "
                "the safe allowlist.\n"
            )

            all_ok = False
            continue

        args = _convert_command_to_args(
            command
        )

        if args is None:

            outputs.append(
                f"$ {command}\n"
                "SKIPPED: unsupported "
                "validation command.\n"
            )

            all_ok = False
            continue

        try:

            completed = subprocess.run(
                args,
                cwd=settings.workspace_dir,
                capture_output=True,
                text=True,
                timeout=(
                    settings
                    .command_timeout_seconds
                ),
                env={
                    **os.environ,
                    "PYTHONDONTWRITEBYTECODE": "1",
                },
            )

            stdout = (
                completed.stdout or ""
            )

            stderr = (
                completed.stderr or ""
            )

            combined = (
                stdout + stderr
            )

            outputs.append(
                f"$ {command}\n"
                f"Python executable: "
                f"{sys.executable}\n"
                f"exit="
                f"{completed.returncode}\n"
                f"{combined[-8000:]}\n"
            )

            if completed.returncode != 0:
                all_ok = False

        except subprocess.TimeoutExpired:

            all_ok = False

            outputs.append(
                f"$ {command}\n"
                f"TIMEOUT after "
                f"{settings.command_timeout_seconds}"
                f" seconds\n"
            )

        except Exception as exc:

            all_ok = False

            outputs.append(
                f"$ {command}\n"
                f"ERROR: {exc}\n"
            )

    return (
        all_ok,
        "\n".join(outputs),
    )