import { AlertCircle, ArrowLeft, Play, RefreshCw } from "lucide-react";
import { useParams, useNavigate } from "react-router-dom";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { ErrorState } from "@/components/ui/error-state";
import { LoadingState } from "@/components/ui/loading-state";
import { PageHeader } from "@/components/ui/page-header";
import { IntelligenceReportCard } from "@/features/jobs/components/intelligence-report";
import { JobStatistics } from "@/features/jobs/components/job-statistics";
import { JobStatusBadge } from "@/features/jobs/components/job-status-badge";
import { OutputDownloadCards } from "@/features/jobs/components/output-download-cards";
import { useJob, useJobIntelligence, useJobReport, useProcessJob } from "@/hooks/use-jobs";
import { useTemplate } from "@/hooks/use-templates";

function formatRelativeTime(dateStr: string): string {
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  if (diffMins < 1) return "just now";
  if (diffMins < 60) return `${diffMins}m ago`;
  const diffHours = Math.floor(diffMins / 60);
  if (diffHours < 24) return `${diffHours}h ago`;
  const diffDays = Math.floor(diffHours / 24);
  return `${diffDays}d ago`;
}

export default function JobDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const {
    data: job,
    isLoading: jobLoading,
    error: jobError,
    isFetching: jobRefetching,
  } = useJob(id);

  const {
    data: report,
    isLoading: reportLoading,
  } = useJobReport(id, job?.status);

  const { data: template } = useTemplate(job?.template_id);
  const processMutation = useProcessJob();

  const canProcess = job?.status === "uploaded";
  const isProcessing = job?.status === "processing" || job?.status === "queued";

  const {
    data: intelligence,
    isLoading: intelligenceLoading,
  } = useJobIntelligence(id, canProcess);

  const isLoading = jobLoading;
  const error = jobError;

  if (isLoading) return <LoadingState message="Loading job..." />;
  if (error || !job) {
    return (
      <ErrorState
        title="Job not found"
        message="Could not load this job. It may have been removed or the ID is invalid."
        retry={() => navigate("/jobs")}
      />
    );
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title={job.original_filename}
        description={`Job ID: ${job.job_id}`}
        actions={
          <div className="flex items-center gap-2">
            {jobRefetching && (
              <RefreshCw className="h-4 w-4 animate-spin text-muted-foreground" />
            )}
            <Button variant="outline" size="sm" onClick={() => navigate("/jobs")}>
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back
            </Button>
          </div>
        }
      />

      <div className="grid gap-6 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Status</CardTitle>
          </CardHeader>
          <CardContent>
            <JobStatusBadge status={job.status} className="text-sm" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Template</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm font-medium">{template?.name || job.template_id}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Created</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm font-medium" suppressHydrationWarning>
              {formatRelativeTime(job.created_at)}
            </p>
          </CardContent>
        </Card>
      </div>

      {canProcess && (
        <Card>
          <CardContent className="pt-6">
            <div className="flex flex-col items-center gap-4 text-center">
              <p className="text-sm text-muted-foreground">This job is ready to be processed.</p>
              <Button
                size="lg"
                disabled={processMutation.isPending}
                onClick={() => processMutation.mutate(job.job_id)}
              >
                {processMutation.isPending ? (
                  <>
                    <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                    Processing...
                  </>
                ) : (
                  <>
                    <Play className="mr-2 h-4 w-4" />
                    Start Processing
                  </>
                )}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {processMutation.isError && (
        <Card className="border-destructive/50">
          <CardHeader>
            <div className="flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-destructive" />
              <CardTitle className="text-destructive">Processing Failed</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-destructive">
              {(processMutation.error as { message?: string })?.message ||
                "An unexpected error occurred during processing."}
            </p>
          </CardContent>
        </Card>
      )}

      {isProcessing && (
        <Card>
          <CardHeader>
            <CardTitle>Processing</CardTitle>
            <CardDescription>Your workbook is being processed</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <RefreshCw className="h-4 w-4 animate-spin" />
              <span>Processing in progress &mdash; this page updates automatically</span>
            </div>
          </CardContent>
        </Card>
      )}

      {reportLoading && (
        <Card>
          <CardHeader>
            <CardTitle>Report</CardTitle>
            <CardDescription>Loading processing results...</CardDescription>
          </CardHeader>
        </Card>
      )}

      {intelligence && canProcess && (
        <IntelligenceReportCard report={intelligence} />
      )}

      {intelligenceLoading && canProcess && (
        <Card>
          <CardHeader>
            <CardTitle>Intelligence Report</CardTitle>
            <CardDescription>Analyzing workbook structure...</CardDescription>
          </CardHeader>
        </Card>
      )}

      {report && (
        <>
          <Card>
            <CardHeader>
              <CardTitle>Report</CardTitle>
              <CardDescription>Processing summary and statistics</CardDescription>
            </CardHeader>
            <CardContent>
              <JobStatistics report={report} />
            </CardContent>
          </Card>

          {report.outputs && report.outputs.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Downloads</CardTitle>
                <CardDescription>Download generated output workbooks</CardDescription>
              </CardHeader>
              <CardContent>
                <OutputDownloadCards jobId={job.job_id} outputs={report.outputs} />
              </CardContent>
            </Card>
          )}
        </>
      )}
    </div>
  );
}
