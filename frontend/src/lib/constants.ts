export const OUTPUT_TYPE_LABELS: Record<string, string> = {
  clean_data: "Clean Data",
  removed_rows: "Removed Rows",
  needs_review: "Needs Review",
  processing_report: "Processing Report",
};

export const OUTPUT_TYPE_API_MAP: Record<string, string> = {
  clean_data: "accepted",
  removed_rows: "rejected",
  needs_review: "review",
  processing_report: "report",
};

export const JOB_STATUS_LABELS: Record<string, string> = {
  uploaded: "Uploaded",
  processing: "Processing",
  completed: "Completed",
  failed: "Failed",
};

export const JOB_STATUS_COLORS: Record<string, string> = {
  uploaded: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  processing: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
  completed: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  failed: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
};
