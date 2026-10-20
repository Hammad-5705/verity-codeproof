"""Command-line interface for VerityAgent CodeProof."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from verity_codeproof import __version__
from verity_codeproof.ai import AIAnalysisError
from verity_codeproof.engine import analyze_diff_text, verify_repository
from verity_codeproof.report import has_failure, render_report


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="verity-codeproof",
        description="Verify code changes with evidence-linked checks and optional AI analysis.",
        epilog=(
            "Safety: tests are not executed unless --run-tests is supplied. "
            "AI provider calls happen only when --ai is supplied."
        ),
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    commands = parser.add_subparsers(dest="command", required=True)

    check = commands.add_parser("check", help="Analyze a Git diff in the current repository.")
    check.add_argument("--root", type=Path, default=Path.cwd(), help="Directory inside the Git worktree.")
    check.add_argument("--base", help="Compare committed changes against this Git ref, e.g. main.")
    check.add_argument(
        "--format",
        choices=("terminal", "markdown", "json", "html"),
        default="terminal",
        help="Report format (default: terminal).",
    )
    check.add_argument("--output", type=Path, help="Write the rendered report to this path.")
    check.add_argument(
        "--run-tests",
        action="store_true",
        help="Explicitly run the repository test suite with pytest (not a sandbox).",
    )
    check.add_argument(
        "--ai",
        action="store_true",
        help="Explicitly send a bounded diff to the configured OpenAI-compatible endpoint.",
    )
    check.add_argument(
        "--fail-on",
        choices=("critical", "high", "medium", "low", "none"),
        default="high",
        help="Return exit code 1 when a finding at or above this severity exists (default: high).",
    )

    demo = commands.add_parser("demo", help="Analyze the included, synthetic demo diff.")
    demo.add_argument(
        "--format",
        choices=("terminal", "markdown", "json", "html"),
        default="terminal",
        help="Report format (default: terminal).",
    )
    demo.add_argument("--output", type=Path, help="Write the rendered report to this path.")
    return parser


def _write_output(text: str, output: Path | None) -> None:
    if output is None:
        print(text)
        return
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text, encoding="utf-8")
    print(f"Report written to {output.resolve()}")


def main(argv: list[str] | None = None) -> int:
    """Run the command line and return a process exit code."""
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "demo":
            fixture = Path(__file__).resolve().parents[2] / "examples" / "demo.diff"
            if not fixture.is_file():
                parser.error("Demo fixture is missing. Run the command from a source checkout.")
            report = analyze_diff_text(fixture.read_text(encoding="utf-8"), project_root="synthetic-demo")
            rendered = render_report(report, args.format)
            _write_output(rendered, args.output)
            return 0

        report = verify_repository(
            start_path=args.root.resolve(),
            base_ref=args.base,
            include_tests=args.run_tests,
            use_ai=args.ai,
        )
        rendered = render_report(report, args.format)
        _write_output(rendered, args.output)
        if args.run_tests and report.tests and report.tests.get("status") != "passed":
            return 1
        return 1 if has_failure(report, args.fail_on) else 0
    except (AIAnalysisError, OSError, RuntimeError, ValueError) as exc:
        print(f"CodeProof error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
