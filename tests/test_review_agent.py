import json
from unittest.mock import MagicMock, patch

from src.github.client import PRFile
from src.models import ReviewResult, Severity
from src.review_agent.agent import (
    _build_diff_content,
    _build_inline_comments,
    _confidence_reasoning,
    _format_summary_comment,
    _parse_llm_response,
    run,
)


class TestBuildDiffContent:
    def test_single_file(self):
        files = [PRFile(filename="app.py", patch="@@ -1 +1 @@\n-old\n+new", status="modified")]
        result = _build_diff_content(files)
        assert "## app.py (modified)" in result
        assert "```diff" in result
        assert "-old" in result
        assert "+new" in result

    def test_multiple_files(self):
        files = [
            PRFile(filename="a.py", patch="+line1", status="added"),
            PRFile(filename="b.py", patch="-line2", status="modified"),
        ]
        result = _build_diff_content(files)
        assert "## a.py (added)" in result
        assert "## b.py (modified)" in result


class TestParseLlmResponse:
    def test_parses_clean_json(self):
        raw = json.dumps({
            "summary": "Clean PR",
            "confidence_score": 5,
            "findings": [],
        })
        result = _parse_llm_response(raw)
        assert result.confidence_score == 5
        assert result.findings == []

    def test_strips_markdown_fences(self):
        raw = '```json\n{"summary": "Test", "confidence_score": 4, "findings": []}\n```'
        result = _parse_llm_response(raw)
        assert result.confidence_score == 4

    def test_parses_findings(self):
        raw = json.dumps({
            "summary": "Found issues",
            "confidence_score": 2,
            "findings": [
                {
                    "file": "src/app.py",
                    "line": 15,
                    "severity": "P0",
                    "category": "security",
                    "description": "Hardcoded secret",
                    "suggested_fix": None,
                },
            ],
        })
        result = _parse_llm_response(raw)
        assert len(result.findings) == 1
        assert result.findings[0].severity == Severity.P0


class TestConfidenceReasoning:
    def test_clean_pr(self):
        result = ReviewResult(summary="Clean", confidence_score=5, findings=[])
        reasons = _confidence_reasoning(result)
        assert any("ready to merge" in r for r in reasons)

    def test_mixed_findings(self):
        result = ReviewResult(
            summary="Issues",
            confidence_score=2,
            findings=[
                {"file": "a.py", "line": 1, "severity": "P0", "category": "security", "description": "x"},
                {"file": "a.py", "line": 2, "severity": "P1", "category": "logic", "description": "y"},
                {"file": "a.py", "line": 3, "severity": "P2", "category": "style", "description": "z"},
            ],
        )
        reasons = _confidence_reasoning(result)
        assert any("critical" in r.lower() for r in reasons)
        assert any("high-severity" in r.lower() for r in reasons)
        assert any("medium-severity" in r.lower() for r in reasons)


class TestFormatSummaryComment:
    def test_greptile_style_header(self):
        result = ReviewResult(summary="All good", confidence_score=5, findings=[])
        comment = _format_summary_comment(result, files_reviewed=3)
        assert "## review-bot Summary" in comment
        assert "## Confidence Score: 5/5" in comment
        assert "3 file(s) reviewed, 0 comment(s)" in comment

    def test_summary_with_findings(self):
        result = ReviewResult(
            summary="Issues found",
            confidence_score=2,
            findings=[
                {
                    "file": "app.py",
                    "line": 10,
                    "severity": "P0",
                    "category": "security",
                    "description": "SQL injection",
                    "suggested_fix": None,
                },
            ],
        )
        comment = _format_summary_comment(result, files_reviewed=1)
        assert "Issues Found" in comment
        assert "SQL injection" in comment
        assert "1 file(s) reviewed, 1 comment(s)" in comment

    def test_issues_in_collapsible_details(self):
        result = ReviewResult(
            summary="x",
            confidence_score=3,
            findings=[
                {"file": "a.py", "line": 1, "severity": "P1", "category": "logic", "description": "Bug"},
            ],
        )
        comment = _format_summary_comment(result, files_reviewed=1)
        assert "<details>" in comment
        assert "</details>" in comment


class TestBuildInlineComments:
    def test_basic_comment(self):
        result = ReviewResult(
            summary="x",
            confidence_score=3,
            findings=[
                {
                    "file": "lib/server.js",
                    "line": 42,
                    "severity": "P1",
                    "category": "logic",
                    "description": "Null pointer dereference",
                    "suggested_fix": None,
                },
            ],
        )
        comments = _build_inline_comments(result)
        assert len(comments) == 1
        assert comments[0]["path"] == "lib/server.js"
        assert comments[0]["line"] == 42
        assert "P1 — High" in comments[0]["body"]
        assert "Null pointer dereference" in comments[0]["body"]

    def test_comment_with_suggestion(self):
        result = ReviewResult(
            summary="x",
            confidence_score=3,
            findings=[
                {
                    "file": "app.py",
                    "line": 5,
                    "severity": "P2",
                    "category": "style",
                    "description": "Use f-string",
                    "suggested_fix": 'f"hello {name}"',
                },
            ],
        )
        comments = _build_inline_comments(result)
        assert "```suggestion" in comments[0]["body"]
        assert 'f"hello {name}"' in comments[0]["body"]


class TestRunIntegration:
    def test_empty_pr_skips_review(self):
        github = MagicMock()
        github.get_pr_files.return_value = []

        result = run(github=github, litellm_api_key="fake-key")

        assert result.confidence_score == 5
        assert result.findings == []
        github.post_comment.assert_not_called()
        github.post_review.assert_not_called()
        github.add_reaction.assert_called_with("eyes")

    @patch("src.review_agent.agent.completion")
    def test_full_review_pipeline(self, mock_completion):
        llm_response = json.dumps({
            "summary": "Added a new endpoint",
            "confidence_score": 3,
            "findings": [
                {
                    "file": "routes/api.js",
                    "line": 25,
                    "severity": "P1",
                    "category": "logic",
                    "description": "Missing error handler",
                    "suggested_fix": None,
                },
            ],
        })
        mock_completion.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content=llm_response))]
        )

        github = MagicMock()
        github.get_pr_files.return_value = [
            PRFile(filename="routes/api.js", patch="@@ +25 @@\n+app.get('/new')", status="modified"),
        ]

        result = run(github=github, litellm_api_key="fake-key")

        assert result.confidence_score == 3
        assert len(result.findings) == 1
        github.post_comment.assert_called_once()
        github.post_review.assert_called_once()
        github.add_reaction.assert_any_call("eyes")
        github.add_reaction.assert_any_call("+1")

        review_call = github.post_review.call_args
        assert review_call.kwargs["event"] == "COMMENT"
        assert len(review_call.kwargs["comments"]) == 1

    @patch("src.review_agent.agent.completion")
    def test_update_description_mode(self, mock_completion):
        llm_response = json.dumps({
            "summary": "Refactored module",
            "confidence_score": 5,
            "findings": [],
        })
        mock_completion.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content=llm_response))]
        )

        github = MagicMock()
        github.get_pr_files.return_value = [
            PRFile(filename="lib/utils.js", patch="@@ +1 @@\n+// clean", status="modified"),
        ]

        run(github=github, litellm_api_key="fake-key", update_description=True)

        github.update_pr_description.assert_called_once()
        github.post_comment.assert_not_called()
