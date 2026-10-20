"""Opt-in repository test execution.

CodeProof does not run project code by default. Test execution is an explicit action and is
not a sandbox; users should inspect unfamiliar repositories and use isolated environments.
"""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path
from typing import Any


def run_pytest(root: Path, timeout_seconds: int = 180) -> dict[str, Any]:
    """Run pytest with a fixed argument vector, bounded runtime, and captured output."""
    started = time.monotonic()
    try:
        completed = subprocess.run(
            [sys.executable, "-m", "pytest", "-q"],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
        output = "\n".join(part for part in (completed.stdout, completed.stderr) if part).strip()
        return {
            "status": "passed" if completed.returncode == 0 else "failed",
            "exit_code": completed.returncode,
            "summary": (
                "pytest completed successfully"
                if completed.returncode == 0
                else "pytest reported failures"
            ),
            "output": output[-12000:],
            "duration_seconds": round(time.monotonic() - started, 3),
        }
    except subprocess.TimeoutExpired as exc:
        partial = exc.stdout or ""
        if isinstance(partial, bytes):
            partial = partial.decode("utf-8", errors="replace")
        return {
            "status": "timed_out",
            "exit_code": None,
            "summary": f"pytest exceeded the {timeout_seconds}-second timeout",
            "output": str(partial)[-12000:],
            "duration_seconds": round(time.monotonic() - started, 3),
        }
    except OSError as exc:
        return {
            "status": "unavailable",
            "exit_code": None,
            "summary": f"Could not start pytest: {exc}",
            "output": "",
            "duration_seconds": round(time.monotonic() - started, 3),
        }
