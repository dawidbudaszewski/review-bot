import logging

import httpx

from src.github.client import GitHubClient
from src.models import ReviewResult

logger = logging.getLogger(__name__)


def run(github: GitHubClient, result: ReviewResult) -> None:
    """Submit a silent APPROVE or REQUEST_CHANGES verdict based on findings.

    Unlike Greptile (which only posts COMMENT reviews), we optionally set
    the PR review status so branch protection rules can gate on it.
    No additional comment body is posted -- the review agent's summary
    and inline comments are the full review output.
    """
    if not result.has_blockers:
        event = "APPROVE"
        logger.info("No blockers found — approving PR.")
    else:
        event = "REQUEST_CHANGES"
        logger.info(
            "Blockers found (P0=%d, P1=%d) — requesting changes.",
            result.p0_count,
            result.p1_count,
        )

    try:
        github.post_review(body="", event=event)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 422:
            logger.warning(
                "Cannot submit %s review (likely self-owned PR), skipping verdict.",
                event,
            )
        else:
            raise
