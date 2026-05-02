import logging
import os
import sys

from src.approval_agent import agent as approval_agent
from src.github.client import GitHubClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> None:
    github_token = os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY")
    pr_number_raw = os.environ.get("PR_NUMBER")

    missing = []
    if not github_token:
        missing.append("GITHUB_TOKEN")
    if not repo:
        missing.append("GITHUB_REPOSITORY")
    if not pr_number_raw:
        missing.append("PR_NUMBER")

    if missing:
        logger.error("Missing required environment variables: %s", ", ".join(missing))
        sys.exit(1)

    pr_number = int(pr_number_raw)  # type: ignore[arg-type]
    logger.info("Starting approval check for %s PR #%d", repo, pr_number)

    github = GitHubClient(token=github_token, repo=repo, pr_number=pr_number)  # type: ignore[arg-type]

    approval_agent.run(github=github)

    logger.info("Approval check complete.")


if __name__ == "__main__":
    main()
