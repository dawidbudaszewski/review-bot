import json
import logging
from pathlib import Path

from litellm import completion

from src.github.client import GitHubClient, PRFile
from src.models import Finding, ReviewResult, Severity, SEVERITY_LABELS

logger = logging.getLogger(__name__)

PROMPT_PATH = Path(__file__).resolve().parent.parent.parent / "prompts" / "review_system.md"

BOT_NAME = "review-bot"


def _build_diff_content(files: list[PRFile]) -> str:
    sections: list[str] = []
    for f in files:
        sections.append(f"## {f.filename} ({f.status})\n\n```diff\n{f.patch}\n```")
    return "\n\n".join(sections)


def _confidence_reasoning(result: ReviewResult) -> list[str]:
    """Generate bullet-point reasoning for the confidence score, like Greptile."""
    reasons: list[str] = []

    if result.p0_count:
        reasons.append(
            f"Found {result.p0_count} critical issue(s) that must be fixed before merging"
        )
    if result.p1_count:
        reasons.append(
            f"Found {result.p1_count} high-severity issue(s) that should be addressed"
        )
    if result.p2_count:
        reasons.append(
            f"{result.p2_count} medium-severity suggestion(s) to consider for code quality"
        )
    if not result.findings:
        reasons.append("No issues found — this PR is ready to merge")

    return reasons


def _format_summary_comment(result: ReviewResult, files_reviewed: int) -> str:
    lines = [
        f"## {BOT_NAME} Summary",
        "",
        result.summary,
        "",
        f"## Confidence Score: {result.confidence_score}/5",
        "",
    ]

    for reason in _confidence_reasoning(result):
        lines.append(f"- {reason}")

    lines.append("")

    if result.findings:
        lines.append("<details>")
        lines.append("<summary>Issues Found</summary>")
        lines.append("")
        lines.append("| Severity | File | Line | Description |")
        lines.append("|----------|------|------|-------------|")
        for f in result.findings:
            lines.append(
                f"| **{f.severity.value}** ({SEVERITY_LABELS[f.severity]}) "
                f"| `{f.file}` | L{f.line} | {f.description} |"
            )
        lines.append("")
        lines.append("</details>")
        lines.append("")

    comment_count = len(result.findings)
    lines.append(f"{files_reviewed} file(s) reviewed, {comment_count} comment(s)")

    return "\n".join(lines)


def _build_inline_comments(result: ReviewResult) -> list[dict]:
    comments: list[dict] = []
    for finding in result.findings:
        badge = f"**[{finding.severity.value} — {SEVERITY_LABELS[finding.severity]}]**"
        body = f"{badge}\n\n{finding.description}"
        if finding.suggested_fix:
            body += f"\n\n```suggestion\n{finding.suggested_fix}\n```"

        comments.append({
            "path": finding.file,
            "line": finding.line,
            "body": body,
        })
    return comments


def _parse_llm_response(raw: str) -> ReviewResult:
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1]
    if cleaned.endswith("```"):
        cleaned = cleaned.rsplit("```", 1)[0]
    return ReviewResult.model_validate(json.loads(cleaned.strip()))


def run(
    github: GitHubClient,
    litellm_api_key: str,
    model: str = "openai/gpt-4o",
    api_base: str | None = None,
    update_description: bool = False,
) -> ReviewResult:
    """Run the review agent: fetch diff, analyze with LLM, post results."""

    logger.info("Reacting with 👀 to indicate analysis started...")
    try:
        github.add_reaction("eyes")
    except Exception:
        logger.warning("Could not add 👀 reaction, continuing anyway.")

    logger.info("Fetching PR files...")
    files = github.get_pr_files()
    if not files:
        logger.info("No files with patches found in PR, skipping review.")
        return ReviewResult(summary="No code changes to review.", confidence_score=5, findings=[])

    logger.info("Analyzing %d files with LLM...", len(files))
    diff_content = _build_diff_content(files)
    system_prompt = PROMPT_PATH.read_text()

    response = completion(
        model=model,
        api_key=litellm_api_key,
        api_base=api_base,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Review the following pull request diff:\n\n{diff_content}"},
        ],
        temperature=0.2,
    )

    raw_output = response.choices[0].message.content
    logger.info("LLM response received, parsing findings...")
    result = _parse_llm_response(raw_output)
    logger.info("Found %d issues (confidence: %d/5)", len(result.findings), result.confidence_score)

    summary_body = _format_summary_comment(result, files_reviewed=len(files))

    if update_description:
        logger.info("Updating PR description with review summary...")
        github.update_pr_description(summary_body)
    else:
        logger.info("Posting PR summary comment...")
        github.post_comment(summary_body)

    inline_comments = _build_inline_comments(result)
    if inline_comments:
        logger.info("Posting %d inline comments...", len(inline_comments))
        github.post_review(body="", event="COMMENT", comments=inline_comments)

    logger.info("Reacting with 👍 to indicate review complete...")
    try:
        github.add_reaction("+1")
    except Exception:
        logger.warning("Could not add 👍 reaction, continuing anyway.")

    return result
