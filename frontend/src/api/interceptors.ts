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
  const status = error.response?.status;
  const originalUrl = error.config?.url || "";

  // 1. Map known status codes to human-readable messages
  let humanMessage = error.response?.data?.error?.message || error.message || "A network error occurred";
  
  if (status === 401) {
    humanMessage = "Your session has expired. Please sign in again.";
  } else if (status === 403) {
    humanMessage = "You don't have permission to perform this action.";
  } else if (status === 404) {
    humanMessage = "The requested resource could not be found.";
  } else if (status === 409) {
    humanMessage = "This operation conflicts with the current state.";
  } else if (status === 422) {
    humanMessage = "Please check the information you provided.";
  } else if (status === 500) {
    humanMessage = "Something went wrong. Please try again.";
  }

  // 2. Global 401 handling for expired sessions
  // Ignore 401s from endpoints where it's expected (e.g. login, register, me)
  const isAuthEndpoint = originalUrl.includes("/auth/login") || 
                         originalUrl.includes("/auth/register") || 
                         originalUrl.includes("/auth/google") || 
                         originalUrl.includes("/auth/me");

  if (status === 401 && !isAuthEndpoint) {
    // Dispatch a global event so useAuth can safely handle the redirect
    // without circular dependencies.
    window.dispatchEvent(new CustomEvent("auth:expired"));
  }

  if (error.response?.data?.error) {
    const apiError = {
      ...error.response.data.error,
      message: humanMessage, // Override with safe message
    };
    return Promise.reject(apiError);
  }

  return Promise.reject({
    code: "network_error",
    message: humanMessage,
    details: {},
  });
}

