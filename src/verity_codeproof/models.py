"""Data models shared by the verification engine and report renderers."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class Finding:
    """A traceable observation about a proposed code change."""

    rule_id: str
    severity: str
    title: str
    message: str
    path: str | None = None
    line: int | None = None
    evidence: str | None = None
    recommendation: str | None = None
    source: str = "heuristic"
    confidence: str = "medium"

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible representation."""
        return asdict(self)


@dataclass
class VerificationReport:
    """Results from one CodeProof verification run."""

    project_root: str
    base_ref: str | None
    changed_files: list[str] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)
    tests: dict[str, Any] | None = None
    ai_analysis: dict[str, Any] | None = None
    generated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="seconds")
    )
    diff_bytes: int = 0
    notes: list[str] = field(default_factory=list)

    @property
    def risk_score(self) -> int:
        """Return a transparent, heuristic score; this is not a probability."""
        weights = {"critical": 40, "high": 25, "medium": 12, "low": 4, "info": 0}
        return min(100, sum(weights.get(item.severity, 0) for item in self.findings))

    @property
    def counts(self) -> dict[str, int]:
        """Count findings by severity."""
        levels = ("critical", "high", "medium", "low", "info")
        return {level: sum(f.severity == level for f in self.findings) for level in levels}

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible report payload."""
        data = asdict(self)
        data["risk_score"] = self.risk_score
        data["counts"] = self.counts
        data["finding_count"] = len(self.findings)
        return data
