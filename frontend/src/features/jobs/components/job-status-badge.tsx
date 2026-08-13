import { cn } from "@/lib/utils";

interface JobStatusBadgeProps {
  status: string;
  className?: string;
}

const statusStyles: Record<string, string> = {
  uploaded: "bg-blue-100 text-blue-700 dark:bg-blue-900/50 dark:text-blue-300",
  queued: "bg-purple-100 text-purple-700 dark:bg-purple-900/50 dark:text-purple-300",
  processing: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/50 dark:text-yellow-300",
  completed: "bg-green-100 text-green-700 dark:bg-green-900/50 dark:text-green-300",
  failed: "bg-red-100 text-red-700 dark:bg-red-900/50 dark:text-red-300",
};

const statusLabels: Record<string, string> = {
  uploaded: "Uploaded",
  queued: "Queued",
  processing: "Processing",
  completed: "Completed",
  failed: "Failed",
};

export function JobStatusBadge({ status, className }: JobStatusBadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium",
        statusStyles[status] || "bg-muted text-muted-foreground",
        className,
      )}
    >
      {(status === "processing" || status === "queued") && (
        <span className="mr-1.5 h-1.5 w-1.5 animate-pulse rounded-full bg-current" />
      )}
      {statusLabels[status] || status}
    </span>
  );
}
