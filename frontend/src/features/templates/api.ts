import { apiGet } from "@/api/helpers";
import type { TemplateDetails, TemplateSummary } from "@/types/api";

export function fetchTemplates() {
  return apiGet<TemplateSummary[]>("/templates");
}

export function fetchTemplate(id: string) {
  return apiGet<TemplateDetails>(`/templates/${id}`);
}
