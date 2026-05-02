import json
import logging
from pathlib import Path

from litellm import completion

from src.github.client import GitHubClient, PRFile
from src.models import Finding, ReviewResult, Severity, SEVERITY_LABELS

logger = logging.getLogger(__name__)

PROMPT_PATH = Path(__file__).resolve().parent.parent.parent / "prompts" / "review_system.md"


def _build_diff_content(files: list[PRFile]) -> str:
    sections: list[str] = []
    for f in files:
        sections.append(f"## {f.filename} ({f.status})\n\n```diff\n{f.patch}\n```")
    return "\n\n".join(sections)


def _format_summary_comment(result: ReviewResult) -> str:
    score = result.confidence_score
    total = len(result.findings)

    lines = [
        "## 🔍 AI Code Review",
        "",
        f"**Confidence Score: {score}/5** — "
        + (
            "Production ready"
            if score == 5
            else "Minor polish needed"
            if score == 4
            else "Implementation issues"
            if score == 3
            else "Significant problems"
            if score == 2
            else "Critical issues found"
        ),
        "",
        result.summary,
        "",
    ]

    if result.findings:
        lines.append(f"### Issues Found ({total})")
        lines.append("")
        lines.append("| Severity | Count |")
        lines.append("|----------|-------|")
        for sev in Severity:
            count = sum(1 for f in result.findings if f.severity == sev)
            if count:
                lines.append(f"| **{sev.value}** ({SEVERITY_LABELS[sev]}) | {count} |")
        lines.append("")

        files_with_issues: dict[str, list[Finding]] = {}
        for finding in result.findings:
            files_with_issues.setdefault(finding.file, []).append(finding)

        lines.append("### File Breakdown")
        lines.append("")
        for file, findings in files_with_issues.items():
            lines.append(f"- **`{file}`** — {len(findings)} issue(s)")
            for f in findings:
                lines.append(f"  - `{f.severity.value}` L{f.line}: {f.description}")
        lines.append("")
    else:
        lines.append("No issues found. This PR looks good to merge! ✅")
        lines.append("")

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


def run(github: GitHubClient, litellm_api_key: str, model: str = "gpt-4o") -> ReviewResult:
    """Run the review agent: fetch diff, analyze with LLM, post results."""
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

    logger.info("Posting PR summary comment...")
    summary_body = _format_summary_comment(result)
    github.post_comment(summary_body)

    inline_comments = _build_inline_comments(result)
    if inline_comments:
        logger.info("Posting %d inline comments...", len(inline_comments))
        github.post_review(body="Detailed findings from AI code review.", event="COMMENT", comments=inline_comments)

    return result
