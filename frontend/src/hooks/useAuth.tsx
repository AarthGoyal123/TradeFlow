/* eslint-disable react-refresh/only-export-components */
import { createContext, useContext, ReactNode, useCallback, useEffect } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { getCurrentUser, logout, User } from "@/api/auth";

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isFetching: boolean;
  error: Error | null;
  refreshUser: () => Promise<void>;
  logoutUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient();

  const { data, isLoading, isFetching, error } = useQuery({
    queryKey: ["currentUser"],
    queryFn: getCurrentUser,
    retry: false, // Don't retry if 401 Unauthorized
  });

  const refreshUser = useCallback(async () => {
    await queryClient.invalidateQueries({ queryKey: ["currentUser"] });
  }, [queryClient]);

  const logoutUser = useCallback(async () => {
    try {
      await logout();
    } finally {
      queryClient.clear();
      window.location.href = "/login";
    }
  }, [queryClient]);

  // Handle global session expiry
  useEffect(() => {
    const handleAuthExpired = () => {
      queryClient.clear(); // Clear stale authenticated data globally
      // Navigate to login if not already there, with error state
      if (window.location.pathname !== "/login") {
        window.location.href = "/login?error=expired_session";
      }
    };

    window.addEventListener("auth:expired", handleAuthExpired);
    return () => window.removeEventListener("auth:expired", handleAuthExpired);
  }, [queryClient]);

  const value = {
    user: data?.user || null,
    isLoading,
    isFetching,
    error: error as Error | null,
    refreshUser,
    logoutUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
