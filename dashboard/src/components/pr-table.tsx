import Link from "next/link";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import {
  ApprovalBadge,
  ConfidenceScore,
  SeverityBadge,
} from "@/components/status-badge";
import type { PRSummary } from "@/lib/github";

function StateBadge({ state }: { state: string }) {
  switch (state) {
    case "merged":
      return (
        <Badge className="bg-purple-100 text-purple-700 hover:bg-purple-100 border-0">
          Merged
        </Badge>
      );
    case "closed":
      return (
        <Badge className="bg-red-50 text-red-600 hover:bg-red-50 border-0">
          Closed
        </Badge>
      );
    default:
      return (
        <Badge className="bg-emerald-50 text-emerald-700 hover:bg-emerald-50 border-0">
          Open
        </Badge>
      );
  }
}

function SeverityCounts({ findings }: { findings: PRSummary["review"]["findings"] }) {
  const p0 = findings.filter((f) => f.severity === "P0").length;
  const p1 = findings.filter((f) => f.severity === "P1").length;
  const p2 = findings.filter((f) => f.severity === "P2").length;

  if (findings.length === 0) {
    return <span className="text-muted-foreground text-sm">--</span>;
  }

  return (
    <div className="flex items-center gap-1.5">
      {p0 > 0 && <SeverityBadge severity="P0" />}
      {p1 > 0 && <SeverityBadge severity="P1" />}
      {p2 > 0 && <SeverityBadge severity="P2" />}
      <span className="text-muted-foreground text-xs ml-0.5">
        {findings.length}
      </span>
    </div>
  );
}

function RelativeTime({ date }: { date: string }) {
  const d = new Date(date);
  const now = new Date();
  const diffMs = now.getTime() - d.getTime();
  const diffMins = Math.floor(diffMs / 60_000);
  const diffHrs = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHrs / 24);

  let text: string;
  if (diffMins < 1) text = "just now";
  else if (diffMins < 60) text = `${diffMins}m ago`;
  else if (diffHrs < 24) text = `${diffHrs}h ago`;
  else text = `${diffDays}d ago`;

  return (
    <time
      dateTime={date}
      title={d.toLocaleString()}
      className="text-muted-foreground text-sm whitespace-nowrap"
    >
      {text}
    </time>
  );
}

export function PRTable({ prs }: { prs: PRSummary[] }) {
  if (prs.length === 0) {
    return (
      <div className="p-12 text-center text-muted-foreground">
        No pull requests found. Make sure GITHUB_REPO is configured correctly.
      </div>
    );
  }

  return (
    <Table>
      <TableHeader>
        <TableRow className="hover:bg-transparent">
          <TableHead className="w-16 pl-6">PR</TableHead>
          <TableHead>Title</TableHead>
          <TableHead className="w-28">Confidence</TableHead>
          <TableHead className="w-40">Findings</TableHead>
          <TableHead className="w-28">Review</TableHead>
          <TableHead className="w-24">State</TableHead>
          <TableHead className="w-24">Updated</TableHead>
          <TableHead className="w-20 pr-6" />
        </TableRow>
      </TableHeader>
      <TableBody>
        {prs.map((pr) => (
          <TableRow key={pr.number} className="group">
            <TableCell className="pl-6">
              <a
                href={pr.htmlUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="font-mono text-xs text-muted-foreground hover:text-foreground transition-colors"
              >
                #{pr.number}
              </a>
            </TableCell>
            <TableCell>
              <div className="flex flex-col">
                <Link
                  href={`/pr/${pr.number}`}
                  className="font-medium text-sm hover:underline underline-offset-4"
                >
                  {pr.title}
                </Link>
                <span className="text-xs text-muted-foreground">
                  {pr.author}
                </span>
              </div>
            </TableCell>
            <TableCell>
              <ConfidenceScore score={pr.review.confidenceScore} />
            </TableCell>
            <TableCell>
              <SeverityCounts findings={pr.review.findings} />
            </TableCell>
            <TableCell>
              <ApprovalBadge status={pr.review.approvalStatus} />
            </TableCell>
            <TableCell>
              <StateBadge state={pr.state} />
            </TableCell>
            <TableCell>
              <RelativeTime date={pr.updatedAt} />
            </TableCell>
            <TableCell className="pr-6">
              <Link
                href={`/pr/${pr.number}`}
                className="text-xs text-muted-foreground opacity-0 group-hover:opacity-100 hover:text-foreground transition-all"
              >
                View &rarr;
              </Link>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
