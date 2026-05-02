import pytest

from src.models import Finding, ReviewResult, Severity


def _make_finding(severity: Severity = Severity.P2, **kwargs) -> Finding:
    defaults = {
        "file": "src/example.py",
        "line": 10,
        "severity": severity,
        "category": "logic",
        "description": "Test issue",
        "suggested_fix": None,
    }
    defaults.update(kwargs)
    return Finding(**defaults)


class TestReviewResult:
    def test_empty_findings_has_no_blockers(self):
        result = ReviewResult(summary="All good", confidence_score=5, findings=[])
        assert result.has_blockers is False

    def test_p2_only_has_no_blockers(self):
        result = ReviewResult(
            summary="Minor issues",
            confidence_score=4,
            findings=[_make_finding(Severity.P2), _make_finding(Severity.P2)],
        )
        assert result.has_blockers is False

    def test_p1_triggers_blocker(self):
        result = ReviewResult(
            summary="Bug found",
            confidence_score=2,
            findings=[_make_finding(Severity.P1)],
        )
        assert result.has_blockers is True

    def test_p0_triggers_blocker(self):
        result = ReviewResult(
            summary="Critical",
            confidence_score=1,
            findings=[_make_finding(Severity.P0)],
        )
        assert result.has_blockers is True

    def test_severity_counts(self):
        result = ReviewResult(
            summary="Mixed",
            confidence_score=2,
            findings=[
                _make_finding(Severity.P0),
                _make_finding(Severity.P0),
                _make_finding(Severity.P1),
                _make_finding(Severity.P2),
                _make_finding(Severity.P2),
                _make_finding(Severity.P2),
            ],
        )
        assert result.p0_count == 2
        assert result.p1_count == 1
        assert result.p2_count == 3

    def test_confidence_score_validation(self):
        with pytest.raises(ValueError):
            ReviewResult(summary="Bad", confidence_score=6, findings=[])

        with pytest.raises(ValueError):
            ReviewResult(summary="Bad", confidence_score=-1, findings=[])

    def test_finding_from_json(self):
        data = {
            "file": "lib/server.js",
            "line": 42,
            "severity": "P0",
            "category": "security",
            "description": "SQL injection vulnerability",
            "suggested_fix": "Use parameterized queries",
        }
        finding = Finding.model_validate(data)
        assert finding.severity == Severity.P0
        assert finding.file == "lib/server.js"
        assert finding.suggested_fix == "Use parameterized queries"
