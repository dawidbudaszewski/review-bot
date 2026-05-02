from unittest.mock import MagicMock

import httpx

from src.approval_agent.agent import (
    _find_review_body,
    _has_blockers,
    _parse_confidence,
    run,
)

CLEAN_REVIEW = """## review-bot Summary

Refactored utility module for better readability.

## Confidence Score: 5/5

- No issues found — this PR is ready to merge

0 file(s) reviewed, 0 comment(s)
"""

REVIEW_WITH_BLOCKERS = """## review-bot Summary

This PR adds a new endpoint with security issues.

## Confidence Score: 1/5

- Found 2 critical issue(s) that must be fixed before merging
- Found 1 high-severity issue(s) that should be addressed

<details>
<summary>Issues Found</summary>

| Severity | File | Line | Description |
|----------|------|------|-------------|
| **P0** (Critical) | `app.py` | L6 | Hardcoded password |
| **P0** (Critical) | `app.py` | L9 | SQL injection |
| **P1** (High) | `app.py` | L16 | Loose equality |

</details>

1 file(s) reviewed, 3 comment(s)
"""

REVIEW_P2_ONLY = """## review-bot Summary

Minor style improvements needed.

## Confidence Score: 4/5

- 2 medium-severity suggestion(s) to consider for code quality

<details>
<summary>Issues Found</summary>

| Severity | File | Line | Description |
|----------|------|------|-------------|
| **P2** (Medium) | `utils.py` | L10 | Unused import |
| **P2** (Medium) | `utils.py` | L25 | Variable naming |

</details>

1 file(s) reviewed, 2 comment(s)
"""


class TestParseConfidence:
    def test_parses_score(self):
        assert _parse_confidence(CLEAN_REVIEW) == 5
        assert _parse_confidence(REVIEW_WITH_BLOCKERS) == 1
        assert _parse_confidence(REVIEW_P2_ONLY) == 4

    def test_returns_none_when_missing(self):
        assert _parse_confidence("No confidence here") is None


class TestHasBlockers:
    def test_no_blockers_in_clean_review(self):
        assert _has_blockers(CLEAN_REVIEW) is False

    def test_detects_p0(self):
        assert _has_blockers(REVIEW_WITH_BLOCKERS) is True

    def test_p2_only_is_not_blocker(self):
        assert _has_blockers(REVIEW_P2_ONLY) is False


class TestFindReviewBody:
    def test_finds_in_pr_description(self):
        github = MagicMock()
        github.get_pr_details.return_value = {"body": CLEAN_REVIEW}

        result = _find_review_body(github)
        assert result == CLEAN_REVIEW
        github.get_comments.assert_not_called()

    def test_finds_in_comments(self):
        github = MagicMock()
        github.get_pr_details.return_value = {"body": "Original PR description"}
        github.get_comments.return_value = [
            {"body": "Some unrelated comment"},
            {"body": REVIEW_WITH_BLOCKERS},
        ]

        result = _find_review_body(github)
        assert result == REVIEW_WITH_BLOCKERS

    def test_returns_none_when_not_found(self):
        github = MagicMock()
        github.get_pr_details.return_value = {"body": "No review here"}
        github.get_comments.return_value = [{"body": "Just a regular comment"}]

        result = _find_review_body(github)
        assert result is None

    def test_handles_null_pr_body(self):
        github = MagicMock()
        github.get_pr_details.return_value = {"body": None}
        github.get_comments.return_value = []

        result = _find_review_body(github)
        assert result is None


class TestApprovalAgentRun:
    def test_approves_clean_review(self):
        github = MagicMock()
        github.get_pr_details.return_value = {"body": CLEAN_REVIEW}

        run(github=github)

        github.post_review.assert_called_once()
        call_kwargs = github.post_review.call_args.kwargs
        assert call_kwargs["event"] == "APPROVE"

    def test_approves_p2_only_review(self):
        github = MagicMock()
        github.get_pr_details.return_value = {"body": REVIEW_P2_ONLY}

        run(github=github)

        github.post_review.assert_called_once()
        call_kwargs = github.post_review.call_args.kwargs
        assert call_kwargs["event"] == "APPROVE"

    def test_does_not_approve_when_blockers(self):
        github = MagicMock()
        github.get_pr_details.return_value = {"body": REVIEW_WITH_BLOCKERS}

        run(github=github)

        github.post_review.assert_not_called()

    def test_skips_when_no_review_found(self):
        github = MagicMock()
        github.get_pr_details.return_value = {"body": "Regular PR"}
        github.get_comments.return_value = []

        run(github=github)

        github.post_review.assert_not_called()

    def test_handles_422_on_self_owned_pr(self):
        github = MagicMock()
        github.get_pr_details.return_value = {"body": CLEAN_REVIEW}
        mock_response = MagicMock()
        mock_response.status_code = 422
        github.post_review.side_effect = httpx.HTTPStatusError(
            "422", request=MagicMock(), response=mock_response
        )

        run(github=github)
        github.post_review.assert_called_once()
