import pytest

from verity_codeproof.ai import AIAnalysisError, analyze_with_ai


def test_ai_requires_explicit_configuration(monkeypatch):
    monkeypatch.delenv("CODEPROOF_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(AIAnalysisError, match="requires"):
        analyze_with_ai("diff --git a/a.py b/a.py")
