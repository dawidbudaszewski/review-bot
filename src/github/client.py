from dataclasses import dataclass

import httpx


@dataclass
class PRFile:
    filename: str
    patch: str
    status: str


class GitHubClient:
    BASE_URL = "https://api.github.com"

    def __init__(self, token: str, repo: str, pr_number: int) -> None:
        self._repo = repo
        self._pr_number = pr_number
        self._http = httpx.Client(
            base_url=self.BASE_URL,
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            timeout=30.0,
        )

    @property
    def _pr_url(self) -> str:
        return f"/repos/{self._repo}/pulls/{self._pr_number}"

    def get_pr_files(self) -> list[PRFile]:
        """Fetch the list of files changed in the PR with their patches."""
        response = self._http.get(f"{self._pr_url}/files", params={"per_page": 100})
        response.raise_for_status()
        return [
            PRFile(
                filename=f["filename"],
                patch=f.get("patch", ""),
                status=f["status"],
            )
            for f in response.json()
            if f.get("patch")
        ]

    def post_comment(self, body: str) -> None:
        """Post a top-level comment on the PR (issue comment)."""
        response = self._http.post(
            f"/repos/{self._repo}/issues/{self._pr_number}/comments",
            json={"body": body},
        )
        response.raise_for_status()

    def post_review(
        self,
        *,
        body: str,
        event: str,
        comments: list[dict] | None = None,
    ) -> None:
        """Submit a PR review with optional inline comments.

        event: APPROVE | REQUEST_CHANGES | COMMENT
        comments: list of {path, line, body} dicts for inline comments
        """
        payload: dict = {"body": body, "event": event}
        if comments:
            payload["comments"] = comments

        response = self._http.post(f"{self._pr_url}/reviews", json=payload)
        response.raise_for_status()

    def get_pr_details(self) -> dict:
        """Fetch basic PR metadata (title, body, head sha, etc.)."""
        response = self._http.get(self._pr_url)
        response.raise_for_status()
        return response.json()

    def update_pr_description(self, body: str) -> None:
        """Update the PR body/description."""
        response = self._http.patch(self._pr_url, json={"body": body})
        response.raise_for_status()

    def add_reaction(self, emoji: str) -> None:
        """Add an emoji reaction to the PR (via the issue reactions API).

        emoji: +1, -1, laugh, confused, heart, hooray, rocket, eyes
        """
        response = self._http.post(
            f"/repos/{self._repo}/issues/{self._pr_number}/reactions",
            json={"content": emoji},
        )
        response.raise_for_status()
