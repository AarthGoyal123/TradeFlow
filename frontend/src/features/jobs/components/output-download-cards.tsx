import { Download } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useDownloadOutput } from "@/hooks/use-jobs";
import type { OutputArtifact } from "@/types/api";
import { OUTPUT_TYPE_API_MAP, OUTPUT_TYPE_LABELS } from "@/lib/constants";

interface OutputDownloadCardsProps {
  jobId: string;
  outputs: OutputArtifact[];
}

export function OutputDownloadCards({ jobId, outputs }: OutputDownloadCardsProps) {
  const download = useDownloadOutput();
  const [downloading, setDownloading] = useState<string | null>(null);

  if (!outputs || outputs.length === 0) return null;

  const handleDownload = (output: OutputArtifact) => {
    const apiType = OUTPUT_TYPE_API_MAP[output.output_type] || output.output_type;
    setDownloading(output.output_type);
    download.mutate(
      { jobId, outputType: apiType, filename: output.filename },
      { onSettled: () => setDownloading(null) },
    );
  };

  return (
    <div className="grid gap-4 sm:grid-cols-2">
      {outputs.map((output) => {
        const isPending = downloading === output.output_type;
        return (
          <Card key={output.output_type}>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm">
                {OUTPUT_TYPE_LABELS[output.output_type] || output.output_type}
              </CardTitle>
              <CardDescription className="truncate text-xs">
                {output.filename}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button
                variant="outline"
                size="sm"
                className="w-full"
                disabled={isPending}
                onClick={() => handleDownload(output)}
                aria-label={`Download ${OUTPUT_TYPE_LABELS[output.output_type] || output.output_type}`}
              >
                <Download className="mr-2 h-4 w-4" />
                {isPending ? "Downloading..." : "Download"}
              </Button>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}
