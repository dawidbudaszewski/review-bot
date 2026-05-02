import { Badge } from "@/components/ui/badge";
import type { ApprovalStatus, Severity } from "@/lib/github";

const approvalConfig: Record<
  ApprovalStatus,
  { label: string; className: string }
> = {
  approved: {
    label: "Approved",
    className: "bg-emerald-100 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-200",
  },
  on_hold: {
    label: "On Hold",
    className: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
  },
  pending: {
    label: "Pending",
    className: "bg-zinc-100 text-zinc-600 dark:bg-zinc-800 dark:text-zinc-300",
  },
};

export function ApprovalBadge({ status }: { status: ApprovalStatus }) {
  const config = approvalConfig[status];
  return (
    <Badge variant="secondary" className={config.className}>
      {config.label}
    </Badge>
  );
}

const severityConfig: Record<Severity, { className: string }> = {
  P0: { className: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200" },
  P1: { className: "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200" },
  P2: { className: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200" },
};

export function SeverityBadge({ severity }: { severity: Severity }) {
  const config = severityConfig[severity];
  return (
    <Badge variant="secondary" className={config.className}>
      {severity}
    </Badge>
  );
}

export function ConfidenceScore({ score }: { score: number | null }) {
  if (score === null) {
    return <span className="text-muted-foreground text-sm">—</span>;
  }

  let colorClass = "text-red-600 dark:text-red-400";
  if (score >= 4) colorClass = "text-emerald-600 dark:text-emerald-400";
  else if (score === 3) colorClass = "text-yellow-600 dark:text-yellow-400";

  return (
    <span className={`font-semibold tabular-nums ${colorClass}`}>
      {score}/5
    </span>
  );
}
