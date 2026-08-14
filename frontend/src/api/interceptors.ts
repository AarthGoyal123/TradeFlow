import type { AxiosError, InternalAxiosRequestConfig } from "axios";

import type { ApiErrorResponse } from "@/types/api";

function getCookie(name: string): string | null {
  const match = document.cookie.match(new RegExp("(^| )" + name + "=([^;]+)"));
  if (match) return decodeURIComponent(match[2]);
  return null;
}

export function requestInterceptor(config: InternalAxiosRequestConfig) {
  const csrfToken = getCookie("csrf_token");
  if (csrfToken) {
    config.headers["X-CSRF-Token"] = csrfToken;
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
