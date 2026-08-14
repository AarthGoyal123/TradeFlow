import { zodResolver } from "@hookform/resolvers/zod";
import { CheckCircle2, Loader2 } from "lucide-react";
import { useCallback, useState } from "react";
import { useForm } from "react-hook-form";
import { useNavigate } from "react-router-dom";
import { z } from "zod";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ErrorState } from "@/components/ui/error-state";
import { FileUpload } from "@/components/ui/file-upload";
import { PageHeader } from "@/components/ui/page-header";
import { Progress } from "@/components/ui/progress";
import { useTemplates } from "@/hooks/use-templates";
import { useUploadJob, useProcessJob } from "@/hooks/use-jobs";

const uploadSchema = z.object({
  template_id: z.string().min(1, "Please select a template"),
});

type UploadForm = z.infer<typeof uploadSchema>;

export default function UploadPage() {
  const navigate = useNavigate();
  const { data: templates, isLoading: templatesLoading, error: templatesError } = useTemplates();
  const upload = useUploadJob();
  const processJob = useProcessJob();
  const [file, setFile] = useState<File | null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [selectedTemplate, setSelectedTemplate] = useState("");

  const {
    handleSubmit,
    formState: { errors },
  } = useForm<UploadForm>({
    resolver: zodResolver(uploadSchema),
    values: { template_id: selectedTemplate },
  });

  const onSubmit = useCallback(
    async () => {
      if (!file || !selectedTemplate) return;
      try {
        const result = await upload.mutateAsync({
          templateId: selectedTemplate,
          file,
          onProgress: setUploadProgress,
        });
        processJob.mutate(result.job_id, {
          onSuccess: (data) => {
            navigate(`/jobs/${data.job_id}`);
          },
          onError: () => {
            // If the queue request fails, we still want to navigate to the job detail
            // where the user can see the status or try again
            navigate(`/jobs/${result.job_id}`);
          }
        });
      } catch {
        // handled by mutation state
      }
    },
    [file, selectedTemplate, upload, navigate, processJob],
  );

  const handleFileSelect = useCallback((selected: File) => {
    setFile(selected);
  }, []);

  const clearFile = useCallback(() => {
    setFile(null);
    setUploadProgress(0);
  }, []);

  if (templatesError) {
    return (
      <ErrorState
        title="Failed to load templates"
        message="Could not fetch available templates. Is the backend running?"
      />
    );
  }

  const isUploading = upload.isPending;

  return (
    <div className="space-y-6">
      <PageHeader title="Upload" description="Upload an Excel workbook for processing" />

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Select Template</CardTitle>
            <CardDescription>Choose the template that matches your workbook format</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <label className="text-sm font-medium">Template</label>
              <select
                value={selectedTemplate}
                onChange={(e) => setSelectedTemplate(e.target.value)}
                disabled={templatesLoading || isUploading}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              >
                <option value="">Select a template...</option>
                {templates?.map((t) => (
                  <option key={t.id} value={t.id}>
                    {t.name} (v{t.version})
                  </option>
                ))}
              </select>
              {errors.template_id && (
                <p className="text-sm text-destructive">{errors.template_id.message}</p>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Upload File</CardTitle>
            <CardDescription>Drop your Excel workbook or click to browse</CardDescription>
          </CardHeader>
          <CardContent>
            {file ? (
              <div className="space-y-4">
                <div className="rounded-lg border bg-muted/50 p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <CheckCircle2 className="h-5 w-5 text-green-500" />
                      <span className="text-sm font-medium">{file.name}</span>
                    </div>
                    <Button variant="ghost" size="sm" onClick={clearFile} disabled={isUploading}>
                      Change
                    </Button>
                  </div>
                  <p className="mt-1 text-xs text-muted-foreground">
                    {(file.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>

                {isUploading && (
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Uploading...</span>
                      <span>{uploadProgress}%</span>
                    </div>
                    <Progress value={uploadProgress} />
                  </div>
                )}

                {upload.isError && (
                  <p className="text-sm text-destructive">
                    {(upload.error as { message?: string })?.message || "Upload failed. Please try again."}
                  </p>
                )}
              </div>
            ) : (
              <FileUpload onFileSelect={handleFileSelect} />
            )}
          </CardContent>
        </Card>
      </div>

      {file && (
        <div className="flex justify-end gap-3">
          <Button variant="outline" onClick={clearFile} disabled={isUploading || processJob.isPending}>
            Cancel
          </Button>
          <Button onClick={handleSubmit(onSubmit)} disabled={isUploading || processJob.isPending || !selectedTemplate}>
            {isUploading || processJob.isPending ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Processing...
              </>
            ) : (
              "Process Workbook"
            )}
          </Button>
        </div>
      )}
    </div>
  );
}
