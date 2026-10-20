"""Orchestration layer for CodeProof checks."""

from __future__ import annotations

from pathlib import Path

from verity_codeproof.ai import analyze_with_ai
from verity_codeproof.git_tools import collect_diff, find_git_root
from verity_codeproof.models import Finding, VerificationReport
from verity_codeproof.runner import run_pytest
from verity_codeproof.scanner import changed_paths, scan_diff


def analyze_diff_text(
    diff_text: str,
    project_root: str = ".",
    base_ref: str | None = None,
) -> VerificationReport:
    """Analyze a provided diff deterministically; useful for tests and integrations."""
    findings = scan_diff(diff_text)
    return VerificationReport(
        project_root=str(Path(project_root).resolve()),
        base_ref=base_ref,
        changed_files=changed_paths(diff_text),
        findings=findings,
        diff_bytes=len(diff_text.encode("utf-8")),
        notes=[
            "Heuristic findings are triage signals, not proof of a vulnerability.",
            "A passing test suite cannot prove that a program is bug-free.",
        ],
    )


def verify_repository(
    start_path: Path,
    base_ref: str | None = None,
    include_tests: bool = False,
    use_ai: bool = False,
) -> VerificationReport:
    """Collect and analyze repository changes."""
    root = find_git_root(start_path)
    diff_text = collect_diff(root, base_ref=base_ref)
    report = analyze_diff_text(diff_text, project_root=str(root), base_ref=base_ref)
    if not diff_text.strip():
        report.notes.append(
            "No diff was found. Stage/commit changes or supply --base with a ref that differs from HEAD."
        )

    if include_tests:
        report.tests = run_pytest(root)
        if report.tests["status"] != "passed":
            report.findings.append(
                Finding(
                    rule_id="test-runner-failed",
                    severity="high",
                    title="Test run did not pass",
                    message=report.tests["summary"],
                    evidence=report.tests.get("output", "")[-500:] or None,
                    recommendation="Review the test output and resolve failures before merging.",
                    source="execution",
                    confidence="high",
                )
            )

    if use_ai:
        ai_findings, metadata = analyze_with_ai(diff_text)
        report.ai_analysis = metadata
        existing = {(f.rule_id, f.path, f.line, f.title) for f in report.findings}
        for finding in ai_findings:
            key = (finding.rule_id, finding.path, finding.line, finding.title)
            if key not in existing:
                report.findings.append(finding)
                existing.add(key)
    return report
