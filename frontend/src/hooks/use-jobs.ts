import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  downloadOutput,
  fetchJob,
  fetchJobIntelligence,
  fetchJobReport,
  triggerProcessing,
  uploadJob,
} from "@/features/jobs/api";

export function useJob(id: string | undefined) {
  return useQuery({
    queryKey: ["jobs", id],
    queryFn: () => fetchJob(id!),
    enabled: !!id,
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      if (status === "processing") return 2000;
      return false;
    },
  });
}

export function useJobReport(id: string | undefined, status?: string) {
  return useQuery({
    queryKey: ["jobs", id, "report"],
    queryFn: () => fetchJobReport(id!),
    enabled: !!id && status === "completed",
    retry: 2,
  });
}

export function useJobIntelligence(jobId: string | undefined, enabled: boolean) {
  return useQuery({
    queryKey: ["job-intelligence", jobId],
    queryFn: () => fetchJobIntelligence(jobId!),
    enabled: !!jobId && enabled,
  });
}

export function useProcessJob() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (jobId: string) => triggerProcessing(jobId),
    onSuccess: (data) => {
      queryClient.setQueryData(["jobs", data.job_id], (old: unknown) => {
        if (old && typeof old === "object" && "status" in old) {
          return { ...old, status: data.status };
        }
        return old;
      });
      queryClient.invalidateQueries({ queryKey: ["jobs", data.job_id] });
      queryClient.invalidateQueries({ queryKey: ["jobs", data.job_id, "report"] });
    },
  });
}

export function useUploadJob() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      templateId,
      file,
      onProgress,
    }: {
      templateId: string;
      file: File;
      onProgress?: (progress: number) => void;
    }) => uploadJob(templateId, file, onProgress),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["jobs"] });
      const recentJobs = JSON.parse(localStorage.getItem("recentJobs") || "[]") as string[];
      const updated = [data.job_id, ...recentJobs.filter((id) => id !== data.job_id)].slice(0, 20);
      localStorage.setItem("recentJobs", JSON.stringify(updated));
    },
  });
}

export function useDownloadOutput() {
  return useMutation({
    mutationFn: ({
      jobId,
      outputType,
      filename,
    }: {
      jobId: string;
      outputType: string;
      filename: string;
    }) => downloadOutput(jobId, outputType, filename),
  });
}
