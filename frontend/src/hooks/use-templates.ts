import { useQuery } from "@tanstack/react-query";

import { fetchTemplate, fetchTemplates } from "@/features/templates/api";

export function useTemplates() {
  return useQuery({
    queryKey: ["templates"],
    queryFn: fetchTemplates,
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
  });
}

export function useTemplate(id: string | undefined) {
  return useQuery({
    queryKey: ["templates", id],
    queryFn: () => fetchTemplate(id!),
    enabled: !!id,
    staleTime: 5 * 60 * 1000,
  });
}
