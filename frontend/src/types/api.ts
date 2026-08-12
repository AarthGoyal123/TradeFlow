export interface ApiError {
  code: string;
  message: string;
  details: Record<string, unknown>;
}

export interface ApiErrorResponse {
  error: ApiError;
}

export interface Job {
  job_id: string;
  template_id: string;
  original_filename: string;
  stored_filename: string;
  status: "uploaded" | "processing" | "completed" | "failed";
  created_at: string;
  updated_at: string;
}

export interface JobUploadResponse {
  job_id: string;
  status: string;
  template_id: string;
  filename: string;
}

export interface ProcessingProgress {
  stage: string;
  status: string;
  message: string;
}

export interface ProcessingIssue {
  code: string;
  message: string;
  details: Record<string, unknown>;
}

export interface ProcessingResponse {
  job_id: string;
  template_id: string;
  status: string;
  progress: ProcessingProgress[];
  errors: ProcessingIssue[];
}

export interface OutputArtifact {
  output_type: string;
  filename: string;
  path: string;
}

export interface JobReport {
  job_id: string;
  template_id: string;
  status: string;
  total_rows: number;
  clean_rows: number;
  removed_rows: number;
  needs_review_rows: number;
  rule_matches: number;
  validation_findings: number;
  outputs: OutputArtifact[];
  created_at: string | null;
}

/* ── Workbook Intelligence Types ── */

export interface ColumnMappingExplanation {
  field: string;
  required: boolean;
  matched: boolean;
  source_header: string | null;
  column_number: number | null;
  confidence: number;
  detection_method: string;
  searched_aliases: string[];
  closest_matches: Array<{ value: string; confidence: number }>;
  suggested_fix: string | null;
}

export interface StructureAnalysis {
  detected_header_row: number | null;
  header_confidence: number;
  total_sheets: number;
  total_columns: number;
  total_data_rows: number;
  structure_confidence: number;
  anomalies: string[];
}

export interface DetectedField {
  label: string;
  column: number;
  sample: string;
  confidence: number;
  reason: string;
}

export interface SemanticAnalysis {
  total_fields_detected: number;
  fields: DetectedField[];
}

export interface DataQuality {
  missing_cells: number;
  empty_rows: number;
  blank_columns: string[];
}

export interface IntelligenceReport {
  structure: StructureAnalysis;
  semantic: SemanticAnalysis;
  data_quality: DataQuality;
  column_mappings: ColumnMappingExplanation[];
  overall_confidence: number;
}

export interface TemplateSummary {
  id: string;
  name: string;
  version: string;
  description: string;
}

export interface TemplateColumn {
  field: string;
  aliases: string[];
  required: boolean;
}

export interface TemplateOutput {
  type: string;
  filename: string;
}

export interface TemplateDetails {
  id: string;
  name: string;
  version: string;
  description: string;
  columns: TemplateColumn[];
  pipeline: string[];
  outputs: TemplateOutput[];
}
