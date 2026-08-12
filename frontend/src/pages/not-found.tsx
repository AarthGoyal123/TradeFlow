import { FileQuestion } from "lucide-react";
import { useNavigate } from "react-router-dom";

import { Button } from "@/components/ui/button";

export default function NotFoundPage() {
  const navigate = useNavigate();

  return (
    <div className="flex min-h-[400px] flex-col items-center justify-center text-center">
      <div className="mb-4 rounded-full bg-muted p-4">
        <FileQuestion className="h-12 w-12 text-muted-foreground" />
      </div>
      <h1 className="text-4xl font-bold">404</h1>
      <p className="mt-2 text-muted-foreground">The page you are looking for does not exist.</p>
      <Button onClick={() => navigate("/")} className="mt-6">
        Go home
      </Button>
    </div>
  );
}
