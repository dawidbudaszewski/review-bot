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
        return

    logger.info("No blockers found — approving PR.")
    try:
        github.post_review(body="", event="APPROVE")
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 422:
            logger.warning("Cannot submit APPROVE (likely self-owned PR), skipping.")
        else:
            raise
