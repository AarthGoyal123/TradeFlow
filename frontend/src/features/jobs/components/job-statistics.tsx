import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { JobReport } from "@/types/api";

interface JobStatisticsProps {
  report: JobReport;
}

const statItems = [
  { key: "total_rows" as const, label: "Total Rows", color: "text-blue-600 dark:text-blue-400" },
  { key: "clean_rows" as const, label: "Accepted", color: "text-green-600 dark:text-green-400" },
  { key: "removed_rows" as const, label: "Removed", color: "text-red-600 dark:text-red-400" },
  {
    key: "needs_review_rows" as const,
    label: "Needs Review",
    color: "text-yellow-600 dark:text-yellow-400",
  },
  {
    key: "rule_matches" as const,
    label: "Rule Matches",
    color: "text-purple-600 dark:text-purple-400",
  },
  {
    key: "validation_findings" as const,
    label: "Validation",
    color: "text-orange-600 dark:text-orange-400",
  },
];

export function JobStatistics({ report }: JobStatisticsProps) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {statItems.map((item) => (
        <Card key={item.key}>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              {item.label}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className={item.color + " text-2xl font-bold"}>
              {report[item.key]}
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
