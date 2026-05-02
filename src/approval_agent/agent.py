import logging
import re

import httpx

from src.github.client import GitHubClient

logger = logging.getLogger(__name__)

REVIEW_BOT_MARKER = "## review-bot Summary"
CONFIDENCE_PATTERN = re.compile(r"Confidence Score:\s*(\d)/5")
BLOCKER_PATTERN = re.compile(r"\*\*P[01]\*\*")


def _find_review_body(github: GitHubClient) -> str | None:
    """Search the PR description and comments for the review bot's output."""
    pr = github.get_pr_details()
    pr_body = pr.get("body") or ""
    if REVIEW_BOT_MARKER in pr_body:
        return pr_body

    for comment in github.get_comments():
        comment_body = comment.get("body", "")
        if REVIEW_BOT_MARKER in comment_body:
            return comment_body

    return None


def _parse_confidence(body: str) -> int | None:
    match = CONFIDENCE_PATTERN.search(body)
    return int(match.group(1)) if match else None


def _has_blockers(body: str) -> bool:
    return bool(BLOCKER_PATTERN.search(body))


def _format_approve_comment(confidence: int | None) -> str:
    score_text = f"{confidence}/5" if confidence is not None else "unknown"
    return (
        "---\n"
        "### :shield: Approval Agent\n"
        "\n"
        f"> **Decision: APPROVED** | Review confidence: {score_text}\n"
        "\n"
        "I've reviewed the code analysis findings and found **no blocking issues** (P0/P1). "
        "This PR is cleared to merge.\n"
        "\n"
        "*— approval-agent (automated)*"
    )


def _format_hold_comment(confidence: int | None) -> str:
    score_text = f"{confidence}/5" if confidence is not None else "unknown"
    return (
        "---\n"
        "### :shield: Approval Agent\n"
        "\n"
        f"> **Decision: ON HOLD** | Review confidence: {score_text}\n"
        "\n"
        "Blocking issues (P0 or P1) were found in the code review. "
        "This PR requires manual review before it can be merged.\n"
        "\n"
        "*— approval-agent (automated)*"
    )


def run(github: GitHubClient) -> None:
    """Read the review bot's posted output from the PR and decide whether to approve.

    Searches the PR description and comments for the review-bot marker,
    parses the confidence score and severity findings from the markdown,
    and submits APPROVE if no P0/P1 blockers are found.
    """
    review_body = _find_review_body(github)

    if review_body is None:
        logger.warning("No review-bot output found on this PR. Skipping approval.")
        return

    confidence = _parse_confidence(review_body)
    blockers = _has_blockers(review_body)

    logger.info("Parsed review: confidence=%s, has_blockers=%s", confidence, blockers)

    if blockers:
        logger.info("P0/P1 issues found in review — not approving. Manual review required.")
        comment = _format_hold_comment(confidence)
        github.post_comment(comment)
        return

    logger.info("No blockers found — approving PR.")
    comment = _format_approve_comment(confidence)
    try:
        github.post_review(body=comment, event="APPROVE")
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 422:
            logger.warning("Cannot submit APPROVE (likely self-owned PR), posting as comment instead.")
            github.post_comment(comment)
        else:
            raise
