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


def test_parse_added_lines_keeps_line_numbers_when_added_line_starts_with_plus_plus():
    diff = """diff --git a/app.py b/app.py
--- a/app.py
+++ b/app.py
@@ -0,0 +1,4 @@
+i = 0
+++x
+++ y
+eval(user_input)
"""
    lines = parse_added_lines(diff)
    assert [(line.path, line.number, line.text) for line in lines] == [
        ("app.py", 1, "i = 0"),
        ("app.py", 2, "++x"),
        ("app.py", 3, "++ y"),
        ("app.py", 4, "eval(user_input)"),
    ]
    assert [(f.rule_id, f.line) for f in scan_diff(diff) if f.rule_id == "dynamic-eval"] == [
        ("dynamic-eval", 4)
    ]


def test_parse_added_lines_ignores_removed_line_that_looks_like_a_file_header():
    diff = """diff --git a/q.py b/q.py
--- a/q.py
+++ b/q.py
@@ -1,3 +1,3 @@
 keep = 1
--- removed content that begins with two dashes
+changed = 2
 tail = 3
"""
    lines = parse_added_lines(diff)
    assert [(line.path, line.number, line.text) for line in lines] == [("q.py", 2, "changed = 2")]


def test_parse_added_lines_handles_multiple_files_without_git_headers():
    diff = """--- a/one.py
+++ b/one.py
@@ -1 +1,2 @@
 a = 1
+b = 2
--- a/two.py
+++ b/two.py
@@ -4,0 +5 @@
+c = 3
"""
    lines = parse_added_lines(diff)
    assert [(line.path, line.number, line.text) for line in lines] == [
        ("one.py", 2, "b = 2"),
        ("two.py", 5, "c = 3"),
    ]


def test_parse_added_lines_ignores_no_newline_marker():
    diff = """diff --git a/m.py b/m.py
--- a/m.py
+++ b/m.py
@@ -1 +1,2 @@
-old = 1
\\ No newline at end of file
+new = 1
+extra = 2
"""
    lines = parse_added_lines(diff)
    assert [(line.number, line.text) for line in lines] == [(1, "new = 1"), (2, "extra = 2")]
