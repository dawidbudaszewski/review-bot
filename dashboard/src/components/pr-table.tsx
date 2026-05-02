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

function SeverityCounts({ findings }: { findings: PRSummary["review"]["findings"] }) {
  const p0 = findings.filter((f) => f.severity === "P0").length;
  const p1 = findings.filter((f) => f.severity === "P1").length;
  const p2 = findings.filter((f) => f.severity === "P2").length;

  if (findings.length === 0) {
    return <span className="text-muted-foreground text-sm">—</span>;
  }

  return (
    <div className="flex gap-1.5">
      {p0 > 0 && <SeverityBadge severity="P0" />}
      {p1 > 0 && <SeverityBadge severity="P1" />}
      {p2 > 0 && <SeverityBadge severity="P2" />}
      <span className="text-muted-foreground text-xs self-center ml-1">
        {findings.length} total
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
    <time dateTime={date} title={d.toLocaleString()} className="text-muted-foreground text-sm whitespace-nowrap">
      {text}
    </time>
  );
}

export function PRTable({ prs }: { prs: PRSummary[] }) {
  if (prs.length === 0) {
    return (
      <div className="rounded-lg border p-12 text-center text-muted-foreground">
        No pull requests found. Make sure GITHUB_REPO is configured correctly.
      </div>
    );
  }

  return (
    <div className="rounded-lg border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-[80px]">PR</TableHead>
            <TableHead>Title</TableHead>
            <TableHead className="w-[120px]">Confidence</TableHead>
            <TableHead className="w-[200px]">Findings</TableHead>
            <TableHead className="w-[120px]">Status</TableHead>
            <TableHead className="w-[100px]">Updated</TableHead>
            <TableHead className="w-[80px]" />
          </TableRow>
        </TableHeader>
        <TableBody>
          {prs.map((pr) => (
            <TableRow key={pr.number}>
              <TableCell>
                <a
                  href={pr.htmlUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="font-mono text-sm text-muted-foreground hover:text-foreground"
                >
                  #{pr.number}
                </a>
              </TableCell>
              <TableCell>
                <div className="flex flex-col gap-0.5">
                  <Link
                    href={`/pr/${pr.number}`}
                    className="font-medium hover:underline"
                  >
                    {pr.title}
                  </Link>
                  <span className="text-xs text-muted-foreground">
                    by {pr.author}
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
                <div className="flex items-center gap-2">
                  <ApprovalBadge status={pr.review.approvalStatus} />
                  <Badge
                    variant="outline"
                    className="text-xs capitalize"
                  >
                    {pr.state}
                  </Badge>
                </div>
              </TableCell>
              <TableCell>
                <RelativeTime date={pr.updatedAt} />
              </TableCell>
              <TableCell>
                <Link
                  href={`/pr/${pr.number}`}
                  className="text-sm text-primary hover:underline"
                >
                  Details →
                </Link>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
