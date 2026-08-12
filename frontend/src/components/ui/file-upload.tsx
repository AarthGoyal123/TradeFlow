import { Upload } from "lucide-react";
import { useCallback, useRef, useState } from "react";

import { cn } from "@/lib/utils";

interface FileUploadProps {
  accept?: string;
  maxSize?: number;
  onFileSelect: (file: File) => void;
  className?: string;
}

export function FileUpload({
  accept = ".xlsx,.xls",
  maxSize = 50 * 1024 * 1024,
  onFileSelect,
  className,
}: FileUploadProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragOver, setDragOver] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const validateAndSelect = useCallback(
    (file: File) => {
      setError(null);
      const ext = "." + file.name.split(".").pop()?.toLowerCase();
      const allowed = accept.split(",").map((e) => e.trim().toLowerCase());
      if (!allowed.includes(ext)) {
        setError(`Invalid file type. Accepted: ${accept}`);
        return;
      }
      if (file.size > maxSize) {
        setError(`File is too large. Maximum: ${Math.round(maxSize / 1024 / 1024)}MB`);
        return;
      }
      onFileSelect(file);
    },
    [accept, maxSize, onFileSelect],
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragOver(false);
      const file = e.dataTransfer.files[0];
      if (file) validateAndSelect(file);
    },
    [validateAndSelect],
  );

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) validateAndSelect(file);
    },
    [validateAndSelect],
  );

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault();
        setDragOver(true);
      }}
      onDragLeave={() => setDragOver(false)}
      onDrop={handleDrop}
      onClick={() => inputRef.current?.click()}
      className={cn(
        "flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed p-8 transition-colors",
        dragOver
          ? "border-primary bg-primary/5"
          : "border-muted-foreground/25 hover:border-muted-foreground/50",
        className,
      )}
    >
      <input
        ref={inputRef}
        type="file"
        accept={accept}
        onChange={handleChange}
        className="hidden"
      />
      <div className="mb-4 rounded-full bg-muted p-3">
        <Upload className="h-6 w-6 text-muted-foreground" />
      </div>
      <p className="text-sm font-medium">Drop your file here, or click to browse</p>
      <p className="mt-1 text-xs text-muted-foreground">
        Accepted: {accept} (up to {Math.round(maxSize / 1024 / 1024)}MB)
      </p>
      {error && <p className="mt-2 text-sm text-destructive">{error}</p>}
    </div>
  );
}
