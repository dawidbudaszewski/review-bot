import { listPRs } from "@/lib/github";
import { PRTable } from "@/components/pr-table";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export const dynamic = "force-dynamic";

export default async function Home() {
  const prs = await listPRs();

  const reviewed = prs.filter((pr) => pr.review.confidenceScore !== null);
  const approved = prs.filter((pr) => pr.review.approvalStatus === "approved");
  const held = prs.filter((pr) => pr.review.approvalStatus === "on_hold");

  return (
    <main className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold tracking-tight">Dashboard</h1>
        <p className="text-sm text-muted-foreground">
          Monitoring PR reviews for{" "}
          <code className="rounded bg-muted px-1.5 py-0.5 font-mono text-xs">
            {process.env.GITHUB_REPO}
          </code>
        </p>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8">
        <StatCard label="Total PRs" value={prs.length} />
        <StatCard label="Reviewed" value={reviewed.length} />
        <StatCard label="Approved" value={approved.length} accent="emerald" />
        <StatCard label="On Hold" value={held.length} accent="red" />
      </div>

      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base font-medium">Pull Requests</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <PRTable prs={prs} />
        </CardContent>
      </Card>
    </main>
  );
}

function StatCard({
  label,
  value,
  accent,
}: {
  label: string;
  value: number;
  accent?: "emerald" | "red";
}) {
  const valueColor =
    accent === "emerald"
      ? "text-emerald-600"
      : accent === "red"
        ? "text-red-600"
        : "text-foreground";

  return (
    <Card>
      <CardContent className="pt-6">
        <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
          {label}
        </p>
        <p className={`mt-1 text-3xl font-bold tabular-nums ${valueColor}`}>
          {value}
        </p>
      </CardContent>
    </Card>
  );
}
