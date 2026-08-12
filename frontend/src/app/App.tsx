import { ErrorBoundary } from "@/components/error-boundary";
import { Providers } from "@/app/providers";

export function App() {
  return (
    <ErrorBoundary>
      <Providers />
    </ErrorBoundary>
  );
}
