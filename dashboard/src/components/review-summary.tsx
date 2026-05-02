import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  ApprovalBadge,
  ConfidenceScore,
  SeverityBadge,
} from "@/components/status-badge";
import type { ReviewData } from "@/lib/github";

export function ReviewSummaryCard({ review }: { review: ReviewData }) {
  const p0 = review.findings.filter((f) => f.severity === "P0").length;
  const p1 = review.findings.filter((f) => f.severity === "P1").length;
  const p2 = review.findings.filter((f) => f.severity === "P2").length;

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      <Card>
        <CardHeader className="pb-2">
          <CardDescription>Confidence</CardDescription>
          <CardTitle className="text-3xl">
            <ConfidenceScore score={review.confidenceScore} />
          </CardTitle>
        </CardHeader>
      </Card>

      <Card>
        <CardHeader className="pb-2">
          <CardDescription>Findings</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {p0 > 0 && (
              <div className="flex items-center gap-1.5">
                <SeverityBadge severity="P0" />
                <span className="text-sm font-medium">&times;{p0}</span>
              </div>
            )}
            {p1 > 0 && (
              <div className="flex items-center gap-1.5">
                <SeverityBadge severity="P1" />
                <span className="text-sm font-medium">&times;{p1}</span>
              </div>
            )}
            {p2 > 0 && (
              <div className="flex items-center gap-1.5">
                <SeverityBadge severity="P2" />
                <span className="text-sm font-medium">&times;{p2}</span>
              </div>
            )}
            {review.findings.length === 0 && (
              <span className="text-sm text-muted-foreground">
                No issues found
              </span>
            )}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-2">
          <CardDescription>Approval Decision</CardDescription>
        </CardHeader>
        <CardContent>
          <ApprovalBadge status={review.approvalStatus} />
        </CardContent>
      </Card>
    </div>
  );
}
