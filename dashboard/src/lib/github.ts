const GITHUB_API = "https://api.github.com";

function headers(): HeadersInit {
  const token = process.env.GITHUB_TOKEN;
  const h: Record<string, string> = {
    Accept: "application/vnd.github+json",
  };
  if (token) h.Authorization = `Bearer ${token}`;
  return h;
}

function repoSlug(): string {
  return process.env.GITHUB_REPO ?? "dawidbudaszewski/fastify";
}

// ─── Types ───────────────────────────────────────────────────────────

export type Severity = "P0" | "P1" | "P2";

export interface Finding {
  severity: Severity;
  file: string;
  line: number;
  description: string;
}

export type ApprovalStatus = "approved" | "on_hold" | "pending";

export interface ReviewData {
  summary: string | null;
  confidenceScore: number | null;
  findings: Finding[];
  approvalStatus: ApprovalStatus;
  approvalComment: string | null;
}

export interface PRSummary {
  number: number;
  title: string;
  author: string;
  state: string;
  createdAt: string;
  updatedAt: string;
  htmlUrl: string;
  headBranch: string;
  baseBranch: string;
  review: ReviewData;
}

// ─── Markdown Parsing ────────────────────────────────────────────────

const REVIEW_BOT_MARKER = "## review-bot Summary";
const APPROVAL_MARKER = "### :shield: Approval Agent";
const CONFIDENCE_RE = /Confidence Score:\s*(\d)\/5/;
const FINDING_ROW_RE =
  /\|\s*\*\*(P\d)\*\*\s*\([^)]*\)\s*\|\s*`([^`]+)`\s*\|\s*L(\d+)\s*\|\s*(.+?)\s*\|/g;

function findReviewBody(prBody: string, comments: GitHubComment[]): string | null {
  if (prBody && prBody.includes(REVIEW_BOT_MARKER)) return prBody;
  for (const c of comments) {
    if (c.body?.includes(REVIEW_BOT_MARKER)) return c.body;
  }
  return null;
}

function findApprovalBody(comments: GitHubComment[]): string | null {
  for (const c of comments) {
    if (c.body?.includes(APPROVAL_MARKER)) return c.body;
  }
  return null;
}

function parseConfidence(body: string): number | null {
  const m = CONFIDENCE_RE.exec(body);
  return m ? parseInt(m[1], 10) : null;
}

function parseFindings(body: string): Finding[] {
  const findings: Finding[] = [];
  let m: RegExpExecArray | null;
  const re = new RegExp(FINDING_ROW_RE.source, FINDING_ROW_RE.flags);
  while ((m = re.exec(body)) !== null) {
    findings.push({
      severity: m[1] as Severity,
      file: m[2],
      line: parseInt(m[3], 10),
      description: m[4].trim(),
    });
  }
  return findings;
}

function parseApprovalStatus(approvalBody: string | null): ApprovalStatus {
  if (!approvalBody) return "pending";
  if (approvalBody.includes("Decision: APPROVED")) return "approved";
  if (approvalBody.includes("Decision: ON HOLD")) return "on_hold";
  return "pending";
}

function extractSummaryText(body: string): string | null {
  const start = body.indexOf(REVIEW_BOT_MARKER);
  if (start === -1) return null;
  const afterMarker = body.slice(start + REVIEW_BOT_MARKER.length).trim();
  const confIdx = afterMarker.indexOf("## Confidence Score:");
  if (confIdx === -1) return afterMarker.split("\n\n")[0].trim() || null;
  return afterMarker.slice(0, confIdx).trim() || null;
}

function buildReviewData(prBody: string, comments: GitHubComment[]): ReviewData {
  const reviewBody = findReviewBody(prBody, comments);
  const approvalBody = findApprovalBody(comments);

  if (!reviewBody) {
    return {
      summary: null,
      confidenceScore: null,
      findings: [],
      approvalStatus: parseApprovalStatus(approvalBody),
      approvalComment: approvalBody,
    };
  }

  return {
    summary: extractSummaryText(reviewBody),
    confidenceScore: parseConfidence(reviewBody),
    findings: parseFindings(reviewBody),
    approvalStatus: parseApprovalStatus(approvalBody),
    approvalComment: approvalBody,
  };
}

// ─── GitHub API ──────────────────────────────────────────────────────

interface GitHubPR {
  number: number;
  title: string;
  state: string;
  body: string | null;
  html_url: string;
  created_at: string;
  updated_at: string;
  head: { ref: string };
  base: { ref: string };
  user: { login: string };
}

interface GitHubComment {
  body: string;
  user: { login: string };
  created_at: string;
}

async function ghFetch<T>(path: string): Promise<T> {
  const res = await fetch(`${GITHUB_API}${path}`, {
    headers: headers(),
    next: { revalidate: 5 },
  });
  if (!res.ok) {
    throw new Error(`GitHub API ${res.status}: ${path}`);
  }
  return res.json() as Promise<T>;
}

export async function listPRs(): Promise<PRSummary[]> {
  const repo = repoSlug();
  const prs = await ghFetch<GitHubPR[]>(
    `/repos/${repo}/pulls?state=all&sort=updated&direction=desc&per_page=30`
  );

  const summaries = await Promise.all(
    prs.map(async (pr) => {
      const comments = await ghFetch<GitHubComment[]>(
        `/repos/${repo}/issues/${pr.number}/comments?per_page=100`
      );
      const review = buildReviewData(pr.body ?? "", comments);

      return {
        number: pr.number,
        title: pr.title,
        author: pr.user.login,
        state: pr.state,
        createdAt: pr.created_at,
        updatedAt: pr.updated_at,
        htmlUrl: pr.html_url,
        headBranch: pr.head.ref,
        baseBranch: pr.base.ref,
        review,
      } satisfies PRSummary;
    })
  );

  return summaries;
}

export async function getPRDetail(prNumber: number): Promise<PRSummary> {
  const repo = repoSlug();
  const pr = await ghFetch<GitHubPR>(`/repos/${repo}/pulls/${prNumber}`);
  const comments = await ghFetch<GitHubComment[]>(
    `/repos/${repo}/issues/${prNumber}/comments?per_page=100`
  );
  const review = buildReviewData(pr.body ?? "", comments);

  return {
    number: pr.number,
    title: pr.title,
    author: pr.user.login,
    state: pr.state,
    createdAt: pr.created_at,
    updatedAt: pr.updated_at,
    htmlUrl: pr.html_url,
    headBranch: pr.head.ref,
    baseBranch: pr.base.ref,
    review,
  };
}
