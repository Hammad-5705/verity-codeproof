from verity_codeproof.engine import analyze_diff_text
from verity_codeproof.report import has_failure, render_html, render_json, render_markdown, render_terminal


def test_report_renderers_include_core_metadata():
    report = analyze_diff_text(
        """diff --git a/app.py b/app.py
--- /dev/null
+++ b/app.py
@@ -0,0 +1 @@
+result = eval(user_input)
""",
        project_root="demo",
        base_ref="main",
    )
    assert "Risk score:" in render_terminal(report)
    assert "dynamic-eval" in render_json(report)
    assert "Findings" in render_markdown(report)
    assert "CodeProof" in render_html(report)


def test_html_escapes_evidence_from_source():
    report = analyze_diff_text(
        """diff --git a/app.py b/app.py
--- /dev/null
+++ b/app.py
@@ -0,0 +1 @@
+value = eval("<script>alert(1)</script>")
"""
    )
    rendered = render_html(report)
    assert '<script>alert(1)</script>' not in rendered
    assert '&lt;script&gt;' in rendered


def test_fail_threshold_is_configurable():
    report = analyze_diff_text(
        """diff --git a/app.py b/app.py
--- /dev/null
+++ b/app.py
@@ -0,0 +1 @@
+value = eval(input())
"""
    )
    assert has_failure(report, "high")
    assert not has_failure(report, "critical")
    assert not has_failure(report, "none")
