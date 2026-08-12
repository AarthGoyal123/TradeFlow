import { AlertCircle, CheckCircle2, HelpCircle } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import type { IntelligenceReport } from "@/types/api";

interface Props {
  report: IntelligenceReport;
}

function confidenceColor(value: number): string {
  if (value >= 0.95) return "text-green-600 dark:text-green-400";
  if (value >= 0.85) return "text-yellow-600 dark:text-yellow-400";
  return "text-red-600 dark:text-red-400";
}

function confidenceBadge(value: number) {
  if (value >= 0.95) return { label: "Auto-mapped", variant: "secondary" as const };
  if (value >= 0.85) return { label: "Suggested", variant: "outline" as const };
  return { label: "Unmatched", variant: "destructive" as const };
}

function MappingRow({ m }: { m: IntelligenceReport["column_mappings"][number] }) {
  const badge = confidenceBadge(m.confidence);
  return (
    <div className="flex items-center justify-between border-b py-2 last:border-0">
      <div className="flex items-center gap-2">
        {m.matched ? (
          <CheckCircle2 className="h-4 w-4 text-green-500" />
        ) : (
          <AlertCircle className="h-4 w-4 text-red-500" />
        )}
        <div>
          <span className="text-sm font-medium">{m.field}</span>
          {m.required && <span className="ml-1 text-xs text-muted-foreground">(required)</span>}
        </div>
      </div>
      <div className="flex items-center gap-2">
        {m.matched ? (
          <span className="text-sm text-muted-foreground">
            {m.source_header}
          </span>
        ) : (
          <span className="text-sm text-muted-foreground">
            {m.suggested_fix ? (
              <span className="text-blue-500">Action needed: {m.suggested_fix}</span>
            ) : m.closest_matches?.length > 0 ? (
              <span>Did you mean: {m.closest_matches[0].value}?</span>
            ) : (
              "No matches found"
            )}
          </span>
        )}
        <Badge variant={badge.variant}>
          {badge.label} ({(m.confidence * 100).toFixed(0)}%)
        </Badge>
      </div>
    </div>
  );
}

export function IntelligenceReportCard({ report }: Props) {
  const hasMappingIssues = report.column_mappings.some((m) => !m.matched);

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Structure Analysis</CardTitle>
          <CardDescription>Header detection & workbook layout</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div>
              <p className="text-sm text-muted-foreground">Header Row</p>
              <p className="text-lg font-bold">{report.structure.detected_header_row ?? "?"}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Sheets</p>
              <p className="text-lg font-bold">{report.structure.total_sheets}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Columns</p>
              <p className="text-lg font-bold">{report.structure.total_columns}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Data Rows</p>
              <p className="text-lg font-bold">{report.structure.total_data_rows}</p>
            </div>
          </div>
          <div className="mt-3">
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">Structure Confidence</span>
              <span className={confidenceColor(report.structure.structure_confidence)}>
                {(report.structure.structure_confidence * 100).toFixed(0)}%
              </span>
            </div>
            <Progress value={report.structure.structure_confidence * 100} className="mt-1" />
          </div>
          {report.structure.anomalies.length > 0 && (
            <div className="mt-3 space-y-1">
              {report.structure.anomalies.map((a, i) => (
                <p key={i} className="flex items-center gap-1 text-sm text-yellow-600 dark:text-yellow-400">
                  <AlertCircle className="h-3 w-3" />
                  {a}
                </p>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {report.semantic.total_fields_detected > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Semantic Detection</CardTitle>
            <CardDescription>
              {report.semantic.total_fields_detected} field{report.semantic.total_fields_detected !== 1 ? "s" : ""} detected by value patterns
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {report.semantic.fields.map((f, i) => (
                <div key={i} className="flex items-center justify-between border-b py-1 last:border-0">
                  <div className="flex items-center gap-2">
                    <HelpCircle className="h-3 w-3 text-blue-500" />
                    <span className="text-sm font-medium">{f.label}</span>
                    <span className="text-xs text-muted-foreground">(col {f.column})</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-muted-foreground">{f.sample}</span>
                    <Badge variant="outline">{(f.confidence * 100).toFixed(0)}%</Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      <Card className={hasMappingIssues ? "border-yellow-500/50" : "border-green-500/50"}>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Column Mappings</CardTitle>
              <CardDescription>
                {hasMappingIssues
                  ? "Some columns could not be auto-mapped — review suggestions below"
                  : "All columns mapped successfully"}
              </CardDescription>
            </div>
            <span className={confidenceColor(report.overall_confidence)}>
              {report.overall_confidence > 0 && `Overall: ${(report.overall_confidence * 100).toFixed(0)}%`}
            </span>
          </div>
        </CardHeader>
        <CardContent>
          {report.column_mappings.map((m, i) => (
            <MappingRow key={i} m={m} />
          ))}
        </CardContent>
      </Card>

      {report.data_quality.missing_cells > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Data Quality</CardTitle>
            <CardDescription>Potential quality issues detected</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 sm:grid-cols-3">
              {report.data_quality.missing_cells > 0 && (
                <div>
                  <p className="text-sm text-muted-foreground">Missing Cells</p>
                  <p className="text-lg font-bold text-yellow-600">{report.data_quality.missing_cells}</p>
                </div>
              )}
              {report.data_quality.empty_rows > 0 && (
                <div>
                  <p className="text-sm text-muted-foreground">Empty Rows</p>
                  <p className="text-lg font-bold text-yellow-600">{report.data_quality.empty_rows}</p>
                </div>
              )}
              {report.data_quality.blank_columns.length > 0 && (
                <div>
                  <p className="text-sm text-muted-foreground">Blank Columns</p>
                  <p className="text-lg font-bold text-yellow-600">{report.data_quality.blank_columns.join(", ")}</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}