/* eslint-disable react-refresh/only-export-components */
import { createContext, useContext, ReactNode, useCallback } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { getCurrentUser, User } from "@/api/auth";

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isFetching: boolean;
  error: Error | null;
  refreshUser: () => Promise<void>;
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

  const value = {
    user: data?.user || null,
    isLoading,
    isFetching,
    error: error as Error | null,
    refreshUser,
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
