from unittest.mock import MagicMock

import httpx

from src.approval_agent.agent import run
from src.models import Finding, ReviewResult, Severity


def _make_finding(severity: Severity, description: str = "Test issue") -> Finding:
    return Finding(
        file="src/app.py",
        line=10,
        severity=severity,
        category="logic",
        description=description,
        suggested_fix=None,
    )


class TestApprovalAgentRun:
    def test_approves_when_no_blockers(self):
        github = MagicMock()
        result = ReviewResult(
            summary="Clean",
            confidence_score=5,
            findings=[_make_finding(Severity.P2)],
        )

        run(github=github, result=result)

        github.post_review.assert_called_once()
        call_kwargs = github.post_review.call_args.kwargs
        assert call_kwargs["event"] == "APPROVE"
        assert call_kwargs["body"] == ""

    def test_requests_changes_when_p0(self):
        github = MagicMock()
        result = ReviewResult(
            summary="Bad",
            confidence_score=1,
            findings=[_make_finding(Severity.P0)],
        )

        run(github=github, result=result)

        github.post_review.assert_called_once()
        call_kwargs = github.post_review.call_args.kwargs
        assert call_kwargs["event"] == "REQUEST_CHANGES"
        assert call_kwargs["body"] == ""

    def test_requests_changes_when_p1(self):
        github = MagicMock()
        result = ReviewResult(
            summary="Bug found",
            confidence_score=2,
            findings=[_make_finding(Severity.P1)],
        )

        run(github=github, result=result)

        call_kwargs = github.post_review.call_args.kwargs
        assert call_kwargs["event"] == "REQUEST_CHANGES"

    def test_requests_changes_with_mixed_severities(self):
        github = MagicMock()
        result = ReviewResult(
            summary="Mixed",
            confidence_score=2,
            findings=[
                _make_finding(Severity.P0),
                _make_finding(Severity.P1),
                _make_finding(Severity.P2),
            ],
        )

        run(github=github, result=result)

        call_kwargs = github.post_review.call_args.kwargs
        assert call_kwargs["event"] == "REQUEST_CHANGES"

    def test_falls_back_on_422_self_owned_pr(self):
        github = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 422
        github.post_review.side_effect = httpx.HTTPStatusError(
            "422", request=MagicMock(), response=mock_response
        )

        result = ReviewResult(
            summary="Bad",
            confidence_score=1,
            findings=[_make_finding(Severity.P0)],
        )

        run(github=github, result=result)
        github.post_review.assert_called_once()
