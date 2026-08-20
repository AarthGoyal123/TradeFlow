import type { AxiosProgressEvent } from "axios";

import { apiClient } from "@/api/client";
import { apiGet, apiPost } from "@/api/helpers";
import type {
  IntelligenceReport,
  Job,
  JobReport,
  JobUploadResponse,
  ProcessingResponse,
} from "@/types/api";

export function fetchJob(id: string) {
  return apiGet<Job>(`/jobs/${id}`);
}

export function fetchJobReport(id: string) {
  return apiGet<JobReport>(`/jobs/${id}/report`);
}

export function fetchJobIntelligence(jobId: string): Promise<IntelligenceReport> {
  return apiGet<IntelligenceReport>(`/jobs/${jobId}/intelligence`);
}

export function triggerProcessing(id: string) {
  return apiPost<ProcessingResponse>(`/jobs/${id}/process`);
}

export async function uploadJob(
  templateId: string,
  file: File,
  onProgress?: (progress: number) => void,
) {
  const formData = new FormData();
  formData.append("template_id", templateId);
  formData.append("file", file);

  const response = await apiClient.post<JobUploadResponse>("/jobs", formData, {
    headers: { "Content-Type": "multipart/form-data" },
    onUploadProgress: (event: AxiosProgressEvent) => {
      if (onProgress && event.total) {
        onProgress(Math.round((event.loaded * 100) / event.total));
      }
    },
  });
  return response.data;
}

export async function downloadOutput(jobId: string, outputType: string, filename: string) {
  const response = await apiClient.get(`/jobs/${jobId}/outputs/${outputType}`, {
    responseType: "blob",
  });
  const url = URL.createObjectURL(response.data);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}
