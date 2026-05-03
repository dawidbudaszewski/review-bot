import { Badge } from "@/components/ui/badge";
import type { TimelineEvent } from "@/lib/github";

const eventConfig: Record<
  TimelineEvent["kind"],
  { icon: string; label: string; color: string; dotColor: string }
> = {
  pr_opened: {
    icon: "📝",
    label: "PR Opened",
    color: "text-foreground",
    dotColor: "bg-blue-500",
  },
  review_bot: {
    icon: "🔍",
    label: "Review Bot",
    color: "text-foreground",
    dotColor: "bg-indigo-500",
  },
  approval_agent: {
    icon: "🛡️",
    label: "Approval Agent",
    color: "text-foreground",
    dotColor: "bg-emerald-500",
  },
  comment: {
    icon: "💬",
    label: "Comment",
    color: "text-foreground",
    dotColor: "bg-zinc-400",
  },
  merged: {
    icon: "🟣",
    label: "Merged",
    color: "text-purple-700",
    dotColor: "bg-purple-500",
  },
  closed: {
    icon: "🔴",
    label: "Closed",
    color: "text-red-600",
    dotColor: "bg-red-500",
  },
};

function formatTime(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
    hour12: true,
  });
}

function truncateBody(body: string, maxLines: number = 6): string {
  const lines = body.split("\n");
  if (lines.length <= maxLines) return body;
  return lines.slice(0, maxLines).join("\n") + "\n…";
}

export function Timeline({ events }: { events: TimelineEvent[] }) {
  if (events.length === 0) {
    return (
      <div className="rounded-lg border p-8 text-center text-muted-foreground">
        No activity recorded.
      </div>
    );
  }

  return (
    <div className="relative">
      <div className="absolute left-[15px] top-2 bottom-2 w-px bg-border" />

      <div className="space-y-0">
        {events.map((event, i) => {
          const config = eventConfig[event.kind];
          const isLast = i === events.length - 1;

          return (
            <div key={i} className="relative flex gap-4 pb-6 last:pb-0">
              <div className="relative z-10 flex flex-col items-center">
                <div
                  className={`h-[10px] w-[10px] mt-1.5 rounded-full ring-4 ring-background ${config.dotColor}`}
                />
                {!isLast && <div className="flex-1" />}
              </div>

              <div className="flex-1 min-w-0 pt-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm">{config.icon}</span>
                  <Badge
                    variant="outline"
                    className="text-xs font-medium px-2 py-0"
                  >
                    {config.label}
                  </Badge>
                  <span className="text-xs text-muted-foreground">
                    {event.actor}
                  </span>
                  <span className="text-xs text-muted-foreground ml-auto">
                    {formatTime(event.timestamp)}
                  </span>
                </div>

                {event.body && (
                  <div className="mt-1.5 rounded-lg border bg-muted/50 p-3">
                    <pre className="text-xs leading-relaxed whitespace-pre-wrap break-words font-mono text-muted-foreground">
                      {truncateBody(event.body)}
                    </pre>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
