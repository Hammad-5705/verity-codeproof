import json

from verity_codeproof.cli import main


def test_demo_command_emits_machine_readable_findings(capsys):
    result = main(["demo", "--format", "json"])
    captured = capsys.readouterr()
    assert result == 0
    payload = json.loads(captured.out)
    assert payload["finding_count"] >= 2
    assert "dynamic-eval" in captured.out
    assert "possible-hardcoded-secret" in captured.out


def test_demo_can_write_a_report_to_disk(tmp_path):
    destination = tmp_path / "reports" / "demo.html"
    result = main(["demo", "--format", "html", "--output", str(destination)])
    assert result == 0
    assert destination.is_file()
    assert "CodeProof verification report" in destination.read_text(encoding="utf-8")
