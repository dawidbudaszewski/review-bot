import { Badge } from "@/components/ui/badge";
import type { ApprovalStatus, Severity } from "@/lib/github";

const approvalConfig: Record<
  ApprovalStatus,
  { label: string; className: string } | null
> = {
  approved: {
    label: "Approved",
    className:
      "bg-emerald-50 text-emerald-700 border-emerald-200 hover:bg-emerald-50",
  },
  on_hold: {
    label: "On Hold",
    className:
      "bg-amber-50 text-amber-700 border-amber-200 hover:bg-amber-50",
  },
  pending: {
    label: "Pending",
    className:
      "bg-zinc-50 text-zinc-500 border-zinc-200 hover:bg-zinc-50",
  },
  none: null,
};

export function ApprovalBadge({ status }: { status: ApprovalStatus }) {
  const config = approvalConfig[status];
  if (!config) {
    return <span className="text-muted-foreground text-sm">--</span>;
  }
  return (
    <Badge variant="outline" className={config.className}>
      {config.label}
    </Badge>
  );
}

const severityConfig: Record<Severity, { className: string }> = {
  P0: {
    className:
      "bg-red-50 text-red-700 border-red-200 hover:bg-red-50",
  },
  P1: {
    className:
      "bg-orange-50 text-orange-700 border-orange-200 hover:bg-orange-50",
  },
  P2: {
    className:
      "bg-yellow-50 text-yellow-700 border-yellow-200 hover:bg-yellow-50",
  },
};

export function SeverityBadge({ severity }: { severity: Severity }) {
  const config = severityConfig[severity];
  return (
    <Badge variant="outline" className={`text-xs ${config.className}`}>
      {severity}
    </Badge>
  );
}

export function ConfidenceScore({ score }: { score: number | null }) {
  if (score === null) {
    return <span className="text-muted-foreground text-sm">--</span>;
  }

  let colorClass = "text-red-600";
  if (score >= 4) colorClass = "text-emerald-600";
  else if (score === 3) colorClass = "text-amber-600";

  return (
    <span className={`font-semibold text-sm tabular-nums ${colorClass}`}>
      {score}/5
    </span>
  );
}
