import { useQueries } from "@tanstack/react-query";
import { Activity, ArrowRight, Search } from "lucide-react";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { PageHeader } from "@/components/ui/page-header";
import { fetchJob } from "@/features/jobs/api";
import { cn } from "@/lib/utils";
import { JOB_STATUS_COLORS, JOB_STATUS_LABELS } from "@/lib/constants";
import type { Job } from "@/types/api";

function getRecentJobIds(): string[] {
  if (typeof window === "undefined") return [];
  return JSON.parse(localStorage.getItem("recentJobs") || "[]");
}

export default function JobsPage() {
  const navigate = useNavigate();
  const [searchId, setSearchId] = useState("");
  const recentIds = getRecentJobIds();

  const recentQueries = useQueries({
    queries: recentIds.map((id) => ({
      queryKey: ["jobs", id],
      queryFn: () => fetchJob(id),
      staleTime: 30_000,
    })),
  });

  const jobs = recentQueries
    .map((q) => q.data)
    .filter((d): d is Job => !!d);

  return (
    <div className="space-y-6">
      <PageHeader title="Jobs" description="View and manage processing jobs" />

      <Card>
        <CardHeader>
          <CardTitle>Look up a Job</CardTitle>
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

      {jobs.length > 0 ? (
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-lg">Recent Jobs</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="divide-y">
              {jobs.map((job) => (
                <div
                  key={job.job_id}
                  className="flex items-center justify-between py-3 first:pt-0 last:pb-0"
                >
                  <div className="flex items-center gap-3">
                    <Activity className="h-4 w-4 text-muted-foreground" />
                    <div>
                      <Link
                        to={`/jobs/${job.job_id}`}
                        className="text-sm font-medium hover:underline"
                      >
                        {job.original_filename}
                      </Link>
                      <div className="flex gap-2 text-xs text-muted-foreground">
                        <span>{job.template_id}</span>
                        <span>&middot;</span>
                        <span className="font-mono">{job.job_id.slice(0, 8)}...</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span
                      className={cn(
                        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium",
                        JOB_STATUS_COLORS[job.status],
                      )}
                    >
                      {JOB_STATUS_LABELS[job.status] || job.status}
                    </span>
                    <Link to={`/jobs/${job.job_id}`}>
                      <Button variant="ghost" size="sm" aria-label="View job details">
                        <ArrowRight className="h-4 w-4" />
                      </Button>
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardContent className="pt-6">
            <EmptyState
              icon={Activity}
              title="No recent jobs"
              description="Upload a workbook to get started"
              action={{ label: "Upload workbook", onClick: () => navigate("/upload") }}
            />
          </CardContent>
        </Card>
      )}
    </div>
  );
}
