"""Small, shell-free Git helpers."""

from __future__ import annotations

import subprocess
from pathlib import Path


class GitError(RuntimeError):
    """Raised when the current directory cannot be reviewed with Git."""


def find_git_root(start: Path) -> Path:
    """Resolve the top-level directory of a Git worktree."""
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=start,
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise GitError(
            "Could not locate a Git worktree. Run this command inside a repository."
        ) from exc
    return Path(completed.stdout.strip()).resolve()


def _git_diff(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "diff", "--no-ext-diff", "--no-color", "--unified=0", *args, "--"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    )
    return completed.stdout


def collect_diff(root: Path, base_ref: str | None = None) -> str:
    """Collect committed, staged, and unstaged changes without invoking a shell."""
    chunks: list[str] = []
    if base_ref:
        try:
            subprocess.run(
                ["git", "rev-parse", "--verify", f"{base_ref}^{{commit}}"],
                cwd=root,
                check=True,
                capture_output=True,
                text=True,
                timeout=10,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            raise GitError(
                f"Base ref {base_ref!r} does not resolve to a commit. Fetch it or choose another ref."
            ) from exc
        chunks.append(_git_diff(root, f"{base_ref}...HEAD"))
    chunks.append(_git_diff(root, "--cached"))
    chunks.append(_git_diff(root))
    return "\n".join(part for part in chunks if part.strip())
