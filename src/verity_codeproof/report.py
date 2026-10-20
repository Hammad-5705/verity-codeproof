"""Accessible report renderers with HTML escaping for source-derived content."""

from __future__ import annotations

import html
import json

from verity_codeproof.models import VerificationReport

_ICONS = {
    "critical": "!!",
    "high": "HIGH",
    "medium": "MED",
    "low": "LOW",
    "info": "INFO",
}


def render_terminal(report: VerificationReport) -> str:
    """Render a compact report suitable for a terminal or CI log."""
    lines = [
        "",
        "VERITYAGENT CODEPROOF",
        "Evidence-first verification report",
        "=" * 58,
        f"Project:       {report.project_root}",
        f"Base ref:      {report.base_ref or 'working tree'}",
        f"Changed files: {len(report.changed_files)}",
        f"Findings:      {len(report.findings)}",
        f"Risk score:    {report.risk_score}/100 (heuristic, not a probability)",
        "-" * 58,
    ]
    if not report.findings:
        lines.append("No heuristic findings in the analyzed diff.")
    for finding in report.findings:
        location = ""
        if finding.path:
            location = finding.path + (f":{finding.line}" if finding.line else "")
            location += " — "
        lines.append(f"[{_ICONS.get(finding.severity, finding.severity.upper())}] {location}{finding.title}")
        lines.append(f"      {finding.message}")
        if finding.recommendation:
            lines.append(f"      Next step: {finding.recommendation}")
    if report.tests:
        lines.extend(
            [
                "-" * 58,
                f"Tests: {report.tests.get('status', 'unknown')} — {report.tests.get('summary', '')}",
                f"Test duration: {report.tests.get('duration_seconds', 0)}s",
            ]
        )
    if report.ai_analysis:
        lines.extend(
            [
                "-" * 58,
                f"AI analysis: {report.ai_analysis.get('status', 'unknown')}",
                "AI output is advisory and must be verified.",
            ]
        )
    for note in report.notes:
        lines.append(f"Note: {note}")
    lines.append("=" * 58)
    return "\n".join(lines)


def render_markdown(report: VerificationReport) -> str:
    """Render a Markdown report for pull requests and CI artifacts."""
    lines = [
        "# VerityAgent CodeProof report",
        "",
        f"- **Generated:** {report.generated_at}",
        f"- **Project:** {report.project_root}",
        f"- **Base ref:** {report.base_ref or 'working tree'}",
        f"- **Changed files:** {len(report.changed_files)}",
        f"- **Findings:** {len(report.findings)}",
        f"- **Risk score:** {report.risk_score}/100 (heuristic, not a probability)",
        "",
        "## Changed files",
        "",
    ]
    if report.changed_files:
        lines.extend(f"- {path}" for path in report.changed_files)
    else:
        lines.append("- No changed file paths were found.")
    lines.extend(["", "## Findings", ""])
    if not report.findings:
        lines.append("No heuristic findings were generated for this diff.")
    for finding in report.findings:
        location = f" — {finding.path}"
        if finding.line:
            location += f":{finding.line}"
        lines.extend(
            [
                f"### [{finding.severity.upper()}] {finding.title}{location if finding.path else ''}",
                "",
                finding.message,
                "",
            ]
        )
        if finding.evidence:
            lines.extend(["Evidence:", "", "~~~text", finding.evidence, "~~~", ""])
        if finding.recommendation:
            lines.extend(["**Suggested next step:** " + finding.recommendation, ""])
        lines.append(
            f"<sub>Source: {finding.source} · Confidence: {finding.confidence} · Rule: {finding.rule_id}</sub>"
        )
        lines.append("")
    if report.tests:
        lines.extend(
            [
                "## Test execution",
                "",
                f"**Status:** {report.tests.get('status', 'unknown')} — {report.tests.get('summary', '')}",
                "",
                "~~~text",
                str(report.tests.get("output", ""))[-12000:],
                "~~~",
                "",
            ]
        )
    if report.ai_analysis:
        lines.extend(
            [
                "## Optional AI analysis",
                "",
                f"- Status: {report.ai_analysis.get('status', 'unknown')}",
                f"- Model: {report.ai_analysis.get('model', 'not specified')}",
                "- AI suggestions require human verification.",
                "",
            ]
        )
    lines.extend(["## Limitations", ""])
    lines.extend(f"- {note}" for note in report.notes)
    lines.append("- CodeProof is a decision-support tool, not a security certification or correctness proof.")
    return "\n".join(lines) + "\n"


def render_json(report: VerificationReport) -> str:
    """Render machine-readable JSON for pipelines."""
    return json.dumps(report.to_dict(), indent=2, ensure_ascii=False) + "\n"


def render_html(report: VerificationReport) -> str:
    """Render a self-contained HTML report; escape every value derived from the repository."""
    color = {
        "critical": "#ff4d6d",
        "high": "#ff7849",
        "medium": "#f5bc42",
        "low": "#60a5fa",
        "info": "#8b9bb4",
    }
    cards = []
    for finding in report.findings:
        location = finding.path or "Repository"
        if finding.line:
            location += f":{finding.line}"
        cards.append(
            '<article class="finding">'
            f'<div class="meta"><span class="pill" style="--sev:{color.get(finding.severity, "#8b9bb4")}">'
            f'{html.escape(finding.severity.upper())}</span><span>{html.escape(location)}</span>'
            f'<span>{html.escape(finding.source)} · {html.escape(finding.confidence)} confidence</span></div>'
            f'<h3>{html.escape(finding.title)}</h3><p>{html.escape(finding.message)}</p>'
            + (f'<pre>{html.escape(finding.evidence)}</pre>' if finding.evidence else "")
            + (
                f'<p class="next"><strong>Suggested next step:</strong> {html.escape(finding.recommendation)}</p>'
                if finding.recommendation
                else ""
            )
            + "</article>"
        )
    if not cards:
        cards.append(
            '<article class="finding"><h3>No heuristic findings</h3>'
            '<p>Review the diff and test results before merging.</p></article>'
        )
    test_block = ""
    if report.tests:
        test_block = (
            '<section class="panel"><h2>Test execution</h2><p><strong>'
            + html.escape(str(report.tests.get("status", "unknown")).upper())
            + "</strong> — "
            + html.escape(str(report.tests.get("summary", "")))
            + "</p><pre>"
            + html.escape(str(report.tests.get("output", ""))[-12000:])
            + "</pre></section>"
        )
    notes = "".join(f"<li>{html.escape(note)}</li>" for note in report.notes)
    test_status = html.escape(str(report.tests.get("status", "not run")).upper() if report.tests else "NOT RUN")
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>CodeProof verification report</title>
<style>
:root{{--bg:#07111f;--panel:#0d1b2d;--border:#24374d;--text:#e8f1fb;--muted:#9bb0c8;--cyan:#4de2d0}}
*{{box-sizing:border-box}}body{{margin:0;background:radial-gradient(ellipse at top right,#12304a 0,transparent 42%),var(--bg);color:var(--text);font:16px/1.6 system-ui,-apple-system,Segoe UI,sans-serif}}
main{{width:min(1000px,calc(100% - 32px));margin:42px auto}}.eyebrow{{color:var(--cyan);letter-spacing:.14em;text-transform:uppercase;font-size:.76rem;font-weight:800}}
h1{{font-size:clamp(2rem,5vw,3.5rem);line-height:1.05;margin:.3rem 0 1rem}}h2{{font-size:1.25rem}}.muted{{color:var(--muted)}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px;margin:24px 0}}
.panel,.finding,.metric{{background:linear-gradient(145deg,#10233a,#0b1727);border:1px solid var(--border);border-radius:16px;padding:18px}}
.metric strong{{display:block;font-size:1.65rem}}.metric span{{color:var(--muted);font-size:.88rem}}.finding{{margin:12px 0}}.meta{{display:flex;gap:10px;flex-wrap:wrap;align-items:center;color:var(--muted);font-size:.82rem}}
.pill{{border:1px solid var(--sev);color:var(--sev);border-radius:999px;padding:2px 9px;font-weight:800;font-size:.7rem}}
pre{{white-space:pre-wrap;overflow-wrap:anywhere;background:#050c15;border:1px solid #203349;padding:12px;border-radius:10px;color:#b6e9e2}}
.next{{border-left:3px solid var(--cyan);padding-left:12px}}footer{{border-top:1px solid var(--border);margin-top:35px;padding-top:18px;color:var(--muted);font-size:.85rem}}
</style></head><body><main>
<div class="eyebrow">VerityAgent · CodeProof</div><h1>Verification report</h1>
<p class="muted">Evidence first. Confidence second. Human judgment always.</p>
<div class="grid">
<div class="metric"><strong>{len(report.changed_files)}</strong><span>Changed files</span></div>
<div class="metric"><strong>{len(report.findings)}</strong><span>Findings</span></div>
<div class="metric"><strong>{report.risk_score}/100</strong><span>Heuristic risk score</span></div>
<div class="metric"><strong>{test_status}</strong><span>Test execution</span></div>
</div>
<section class="panel"><h2>Run context</h2><p><strong>Project:</strong> {html.escape(report.project_root)}</p>
<p><strong>Base ref:</strong> {html.escape(report.base_ref or "working tree")}</p>
<p><strong>Generated:</strong> {html.escape(report.generated_at)}</p></section>
<section><h2>Findings</h2>{''.join(cards)}</section>{test_block}
<section class="panel"><h2>Important limitations</h2><ul>{notes}<li>CodeProof is a decision-support tool, not a security certification or correctness proof.</li></ul></section>
<footer>Generated locally by VerityAgent CodeProof. Verify recommendations before applying changes.</footer>
</main></body></html>"""


def render_report(report: VerificationReport, output_format: str) -> str:
    """Render a report in the selected output format."""
    renderers = {
        "terminal": render_terminal,
        "markdown": render_markdown,
        "json": render_json,
        "html": render_html,
    }
    try:
        renderer = renderers[output_format]
    except KeyError as exc:
        raise ValueError(f"Unsupported report format: {output_format}") from exc
    return renderer(report)


def has_failure(report: VerificationReport, fail_on: str) -> bool:
    """Return true if a finding meets the configured severity threshold."""
    thresholds = {"critical": 4, "high": 3, "medium": 2, "low": 1, "none": 99}
    if fail_on == "none":
        return False
    minimum = thresholds[fail_on]
    levels = {"critical": 4, "high": 3, "medium": 2, "low": 1, "info": 0}
    return any(levels.get(f.severity, 0) >= minimum for f in report.findings)
