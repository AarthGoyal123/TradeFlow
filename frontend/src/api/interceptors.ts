import type { AxiosError, InternalAxiosRequestConfig } from "axios";

import type { ApiErrorResponse } from "@/types/api";

export function requestInterceptor(config: InternalAxiosRequestConfig) {
  const token = localStorage.getItem("auth_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}

export function responseErrorInterceptor(error: AxiosError<ApiErrorResponse>) {
  if (error.response?.data?.error) {
    const apiError = error.response.data.error;
    return Promise.reject(apiError);
  }
  return Promise.reject({
    code: "network_error",
    message: error.message || "A network error occurred",
    details: {},
  });
}
