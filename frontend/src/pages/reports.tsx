import { useQueries } from "@tanstack/react-query";
import { BarChart3, Search, FileText } from "lucide-react";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { PageHeader } from "@/components/ui/page-header";
import { fetchJobReport } from "@/features/jobs/api";
import { OUTPUT_TYPE_LABELS } from "@/lib/constants";
import type { JobReport } from "@/types/api";

function getRecentJobIds(): string[] {
  if (typeof window === "undefined") return [];
  return JSON.parse(localStorage.getItem("recentJobs") || "[]");
}

export default function ReportsPage() {
  const navigate = useNavigate();
  const [searchId, setSearchId] = useState("");
  const recentIds = getRecentJobIds();

  const reportQueries = useQueries({
    queries: recentIds.map((id) => ({
      queryKey: ["jobs", id, "report"],
      queryFn: () => fetchJobReport(id),
      staleTime: 60_000,
      retry: 1,
    })),
  });

  const reports = reportQueries
    .map((q) => q.data)
    .filter((d): d is JobReport => !!d);

  return (
    <div className="space-y-6">
      <PageHeader title="Reports" description="View processing reports and statistics" />

      <Card>
        <CardHeader>
          <CardTitle>Look up a Report</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-3">
            <input
              type="text"
              placeholder="Enter Job ID..."
              value={searchId}
              onChange={(e) => setSearchId(e.target.value)}
              className="flex h-10 flex-1 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
            />
            <Link to={searchId.trim() ? `/jobs/${searchId.trim()}` : "#"}>
              <Button disabled={!searchId.trim()}>
                <Search className="mr-2 h-4 w-4" />
                View
              </Button>
            </Link>
          </div>
        </CardContent>
      </Card>

      {reports.length > 0 ? (
        <div className="space-y-4">
          {reports.map((report) => (
            <Link key={report.job_id} to={`/jobs/${report.job_id}`}>
              <Card className="transition-colors hover:bg-accent/50">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-sm font-medium">
                      <code className="rounded bg-muted px-1.5 py-0.5 text-xs">
                        {report.job_id.slice(0, 12)}...
                      </code>
                    </CardTitle>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="grid gap-4 sm:grid-cols-3">
                    <div>
                      <p className="text-xs text-muted-foreground">Total Rows</p>
                      <p className="text-lg font-semibold">{report.total_rows}</p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Accepted</p>
                      <p className="text-lg font-semibold text-green-600 dark:text-green-400">
                        {report.clean_rows}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Needs Review</p>
                      <p className="text-lg font-semibold text-yellow-600 dark:text-yellow-400">
                        {report.needs_review_rows}
                      </p>
                    </div>
                  </div>
                  {report.outputs && report.outputs.length > 0 && (
                    <div className="mt-3 flex flex-wrap gap-2">
                      {report.outputs.map((o) => (
                        <span
                          key={o.output_type}
                          className="inline-flex items-center gap-1 rounded-full bg-muted px-2.5 py-0.5 text-xs text-muted-foreground"
                        >
                          <FileText className="h-3 w-3" />
                          {OUTPUT_TYPE_LABELS[o.output_type] || o.output_type}
                        </span>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      ) : (
        <Card>
          <CardContent className="pt-6">
            <EmptyState
              icon={BarChart3}
              title="No reports yet"
              description="Process a workbook to generate reports"
              action={{ label: "Upload workbook", onClick: () => navigate("/upload") }}
            />
          </CardContent>
        </Card>
      )}
    </div>
  );
}
