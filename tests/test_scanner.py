from verity_codeproof.scanner import changed_paths, parse_added_lines, scan_diff


def test_parse_added_lines_tracks_new_file_line_numbers():
    diff = """diff --git a/app.py b/app.py
index 123..456 100644
--- a/app.py
+++ b/app.py
@@ -2,0 +3,2 @@
+value = eval(user_input)
+print(value)
"""
    lines = parse_added_lines(diff)
    assert [(line.path, line.number, line.text) for line in lines] == [
        ("app.py", 3, "value = eval(user_input)"),
        ("app.py", 4, "print(value)"),
    ]


def test_changed_paths_lists_new_side_paths():
    diff = """diff --git a/src/app.py b/src/app.py
--- a/src/app.py
+++ b/src/app.py
@@ -1 +1 @@
-old = 1
+new = 2
"""
    assert changed_paths(diff) == ["src/app.py"]


def test_scanner_finds_eval_and_credential_like_literal():
    diff = """diff --git a/src/example.py b/src/example.py
--- /dev/null
+++ b/src/example.py
@@ -0,0 +1,2 @@
+result = eval(user_input)
+API_KEY = "NOT_A_REAL_SECRET_BUT_LOOKS_SENSITIVE_123456"
"""
    findings = scan_diff(diff)
    rules = {finding.rule_id for finding in findings}
    assert "dynamic-eval" in rules
    assert "possible-hardcoded-secret" in rules
    assert all(finding.path == "src/example.py" for finding in findings)
    secret_finding = next(f for f in findings if f.rule_id == "possible-hardcoded-secret")
    assert secret_finding.evidence == "credential-like value [redacted]"
    assert "NOT_A_REAL_SECRET" not in (secret_finding.evidence or "")


def test_comments_are_not_scanned_as_executable_lines():
    diff = """diff --git a/tests/test_app.py b/tests/test_app.py
--- /dev/null
+++ b/tests/test_app.py
@@ -0,0 +1 @@
+# eval(user_input) is unsafe
"""
    assert scan_diff(diff) == []


def test_production_python_without_test_path_gets_info_prompt():
    diff = """diff --git a/src/service.py b/src/service.py
--- a/src/service.py
+++ b/src/service.py
@@ -0,0 +1 @@
+def work():
"""
    findings = scan_diff(diff)
    assert any(item.rule_id == "test-change-not-detected" for item in findings)
    assert all(item.severity == "info" for item in findings)
