from dataclasses import dataclass, field
from typing import List


@dataclass
class GuardrailResult:
    passed: bool
    severity: str = "none"
    evidence: List[str] = field(default_factory=list)
    message: str = ""

    def to_dict(self):
        return {
            "passed": self.passed,
            "severity": self.severity,
            "evidence": self.evidence,
            "message": self.message,
        }


SEVERITY_ORDER = ["none", "low", "medium", "high", "critical"]


def worst_severity(*severities: str) -> str:
    return max(severities, key=lambda s: SEVERITY_ORDER.index(s) if s in SEVERITY_ORDER else 0)
