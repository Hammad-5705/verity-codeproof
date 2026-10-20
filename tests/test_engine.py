from verity_codeproof.engine import analyze_diff_text


def test_risk_score_is_bounded_and_transparent():
    report = analyze_diff_text(
        """diff --git a/app.py b/app.py
--- /dev/null
+++ b/app.py
@@ -0,0 +1,2 @@
+eval(user_input)
+subprocess.run(command, shell=True)
"""
    )
    assert 0 <= report.risk_score <= 100
    assert report.counts["high"] >= 1


def test_empty_diff_produces_clean_report():
    report = analyze_diff_text("")
    assert report.changed_files == []
    assert report.findings == []
    assert report.risk_score == 0
