import { useQueries } from "@tanstack/react-query";
import { Activity, ArrowRight, Briefcase, FileSpreadsheet, Upload as UploadIcon } from "lucide-react";
import { Link } from "react-router-dom";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { PageHeader } from "@/components/ui/page-header";
import { fetchJob } from "@/features/jobs/api";
import { useTemplates } from "@/hooks/use-templates";
import { cn } from "@/lib/utils";
import { JOB_STATUS_COLORS, JOB_STATUS_LABELS } from "@/lib/constants";
import type { Job } from "@/types/api";

function getRecentJobIds(): string[] {
  if (typeof window === "undefined") return [];
  return JSON.parse(localStorage.getItem("recentJobs") || "[]");
}

export default function DashboardPage() {
  const { data: templates } = useTemplates();
  const recentIds = getRecentJobIds().slice(0, 5);

  const recentJobs = useQueries({
    queries: recentIds.map((id) => ({
      queryKey: ["jobs", id],
      queryFn: () => fetchJob(id),
      staleTime: 30_000,
    })),
  });

  const jobData = recentJobs
    .map((q) => q.data)
    .filter((d): d is Job => !!d);

  return (
    <div className="space-y-8">
      <PageHeader title="Dashboard" description="Overview of your processing activity" />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Templates</CardTitle>
            <FileSpreadsheet className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{templates?.length ?? "--"}</div>
            <p className="text-xs text-muted-foreground">Available templates</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Quick Upload</CardTitle>
            <UploadIcon className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <Link to="/upload">
              <Button variant="default" size="sm" className="w-full">
                Upload workbook
              </Button>
            </Link>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Jobs</CardTitle>
            <Briefcase className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <Link to="/jobs">
              <Button variant="outline" size="sm" className="w-full">
                View all jobs
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>

      {templates && templates.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Available Templates</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="divide-y">
              {templates.map((t) => (
                <div key={t.id} className="flex items-center justify-between py-3 first:pt-0 last:pb-0">
                  <div>
                    <p className="text-sm font-medium">{t.name}</p>
                    <p className="text-xs text-muted-foreground">{t.description}</p>
                  </div>
                  <Badge variant="secondary" className="text-xs">
                    v{t.version}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {jobData.length > 0 && (
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-lg">Recent Uploads</CardTitle>
            <Link
              to="/jobs"
              className="flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground"
            >
              View all <ArrowRight className="h-3 w-3" />
            </Link>
          </CardHeader>
          <CardContent>
            <div className="divide-y">
              {jobData.map((job) => (
                <div key={job.job_id} className="flex items-center justify-between py-3 first:pt-0 last:pb-0">
                  <div className="flex items-center gap-3">
                    <Activity className="h-4 w-4 text-muted-foreground" />
                    <div>
                      <Link
                        to={`/jobs/${job.job_id}`}
                        className="text-sm font-medium hover:underline"
                      >
                        {job.original_filename}
                      </Link>
                      <p className="text-xs text-muted-foreground">{job.template_id}</p>
                    </div>
                  </div>
                  <span
                    className={cn(
                      "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium",
                      JOB_STATUS_COLORS[job.status],
                    )}
                  >
                    {JOB_STATUS_LABELS[job.status] || job.status}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
