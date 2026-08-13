import { apiClient } from "./client";

export interface User {
  id: string;
  email: string;
  display_name: string;
}

export interface AuthResponse {
  user: User;
}

export async function login(credentials: Record<string, string>): Promise<void> {
  await apiClient.post("/auth/login", credentials);
}

export async function register(data: Record<string, string>): Promise<void> {
  await apiClient.post("/auth/register", data);
}

export async function logout(): Promise<void> {
  await apiClient.post("/auth/logout");
}

export async function getCurrentUser(): Promise<AuthResponse> {
  const { data } = await apiClient.get<AuthResponse>("/auth/me");
  return data;
}
