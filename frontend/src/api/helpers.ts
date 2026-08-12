import { apiClient } from "@/api/client";
import type { ApiRequestConfig } from "@/api/types";

export async function apiRequest<TResponse, TData = unknown>(
  config: ApiRequestConfig<TData>,
): Promise<TResponse> {
  const response = await apiClient.request<TResponse>(config);
  return response.data;
}

export async function apiGet<TResponse>(url: string) {
  return apiRequest<TResponse>({ method: "GET", url });
}

export async function apiPost<TResponse, TData = unknown>(url: string, data?: TData) {
  return apiRequest<TResponse, TData>({ method: "POST", url, data });
}
