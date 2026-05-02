from enum import Enum

from pydantic import BaseModel, Field


class Severity(str, Enum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"


SEVERITY_LABELS: dict[Severity, str] = {
    Severity.P0: "Critical",
    Severity.P1: "High",
    Severity.P2: "Medium",
}


class Finding(BaseModel):
    file: str = Field(description="Relative path of the file containing the issue")
    line: int = Field(description="Line number in the diff where the issue is found")
    severity: Severity = Field(description="P0 = critical, P1 = high, P2 = medium")
    category: str = Field(description="Category: logic, security, performance, style, or syntax")
    description: str = Field(description="Clear explanation of the issue")
    suggested_fix: str | None = Field(default=None, description="Suggested code fix, if applicable")


class ReviewResult(BaseModel):
    summary: str = Field(description="Plain-language summary of what the PR does and key issues found")
    confidence_score: int = Field(ge=0, le=5, description="0-5 merge readiness score")
    findings: list[Finding] = Field(default_factory=list, description="List of issues found in the PR")

    @property
    def has_blockers(self) -> bool:
        return any(f.severity in (Severity.P0, Severity.P1) for f in self.findings)

    @property
    def p0_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == Severity.P0)

    @property
    def p1_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == Severity.P1)

    @property
    def p2_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == Severity.P2)
