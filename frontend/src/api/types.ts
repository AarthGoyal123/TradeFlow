import type { AxiosRequestConfig } from "axios";

export type HttpMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE";

export interface ApiRequestConfig<TData = unknown> extends AxiosRequestConfig {
  method: HttpMethod;
  url: string;
  data?: TData;
}
