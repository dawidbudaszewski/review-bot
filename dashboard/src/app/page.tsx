import { listPRs } from "@/lib/github";
import { PRTable } from "@/components/pr-table";

export const dynamic = "force-dynamic";

export default async function Home() {
  const prs = await listPRs();

  const reviewed = prs.filter((pr) => pr.review.confidenceScore !== null);
  const approved = prs.filter((pr) => pr.review.approvalStatus === "approved");
  const held = prs.filter((pr) => pr.review.approvalStatus === "on_hold");

  return (
    <main className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-10">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">Review Bot Dashboard</h1>
        <p className="mt-1 text-muted-foreground">
          PR review and approval agent runs for{" "}
          <code className="text-sm bg-muted px-1.5 py-0.5 rounded">
            {process.env.GITHUB_REPO}
          </code>
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 mb-8">
        <StatCard label="Total PRs" value={prs.length} />
        <StatCard label="Reviewed" value={reviewed.length} />
        <StatCard label="Approved" value={approved.length} accent="emerald" />
        <StatCard label="On Hold" value={held.length} accent="red" />
      </div>

      <PRTable prs={prs} />
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
      ? "text-emerald-600 dark:text-emerald-400"
      : accent === "red"
        ? "text-red-600 dark:text-red-400"
        : "text-foreground";

  return (
    <div className="rounded-lg border bg-card p-4">
      <p className="text-sm text-muted-foreground">{label}</p>
      <p className={`text-2xl font-bold tabular-nums ${valueColor}`}>
        {value}
      </p>
    </div>
  );
}
