import logging

from src.github.client import GitHubClient
from src.models import ReviewResult, Severity, SEVERITY_LABELS

logger = logging.getLogger(__name__)


def _format_verdict(result: ReviewResult) -> str:
    if not result.has_blockers:
        return (
            f"## ✅ Approved\n\n"
            f"Confidence: **{result.confidence_score}/5**\n\n"
            f"No critical or high-severity issues found. "
            f"{'There are ' + str(result.p2_count) + ' medium-severity suggestions to consider.' if result.p2_count else 'This PR is clean.'}"
        )

    lines = [
        "## ❌ Changes Requested",
        "",
        f"Confidence: **{result.confidence_score}/5**",
        "",
        "The following blocking issues must be resolved before merging:",
        "",
    ]

    for finding in result.findings:
        if finding.severity in (Severity.P0, Severity.P1):
            lines.append(
                f"- **{finding.severity.value}** ({SEVERITY_LABELS[finding.severity]}) "
                f"in `{finding.file}` L{finding.line}: {finding.description}"
            )

    lines.append("")
    lines.append("Please address the above issues and push a new commit.")

    return "\n".join(lines)


def run(github: GitHubClient, result: ReviewResult) -> None:
    """Evaluate the review result and submit an approval or request-changes verdict."""
    if not result.has_blockers:
        logger.info("No blockers found — approving PR.")
        verdict = _format_verdict(result)
        github.post_review(body=verdict, event="APPROVE")
    else:
        logger.info(
            "Blockers found (P0=%d, P1=%d) — requesting changes.",
            result.p0_count,
            result.p1_count,
        )
        verdict = _format_verdict(result)
        github.post_review(body=verdict, event="REQUEST_CHANGES")
