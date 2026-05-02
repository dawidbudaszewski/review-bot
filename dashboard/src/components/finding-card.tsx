import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { SeverityBadge } from "@/components/status-badge";
import type { Finding } from "@/lib/github";

export function FindingsTable({ findings }: { findings: Finding[] }) {
  if (findings.length === 0) {
    return (
      <div className="rounded-lg border p-8 text-center text-muted-foreground">
        No issues found in this review.
      </div>
    );
  }

  return (
    <div className="rounded-lg border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-[80px]">Severity</TableHead>
            <TableHead className="w-[250px]">File</TableHead>
            <TableHead className="w-[80px]">Line</TableHead>
            <TableHead>Description</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {findings.map((f, i) => (
            <TableRow key={i}>
              <TableCell>
                <SeverityBadge severity={f.severity} />
              </TableCell>
              <TableCell>
                <code className="text-sm bg-muted px-1.5 py-0.5 rounded break-all">
                  {f.file}
                </code>
              </TableCell>
              <TableCell>
                <span className="font-mono text-sm text-muted-foreground">
                  L{f.line}
                </span>
              </TableCell>
              <TableCell className="text-sm">{f.description}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
