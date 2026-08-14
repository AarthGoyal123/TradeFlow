/* eslint-disable react-refresh/only-export-components */

import { lazy, Suspense, useEffect, useRef } from "react";
import { createBrowserRouter } from "react-router-dom";

import { ErrorBoundary } from "@/components/error-boundary";
import { LoadingState } from "@/components/ui/loading-state";
import { RootLayout } from "@/layouts/root-layout";

const DashboardPage = lazy(() => import("@/pages/dashboard"));
const UploadPage = lazy(() => import("@/pages/upload"));
const JobsPage = lazy(() => import("@/pages/jobs"));
const JobDetailPage = lazy(() => import("@/pages/job-detail"));
const ReportsPage = lazy(() => import("@/pages/reports"));
const SettingsPage = lazy(() => import("@/pages/settings"));
const NotFoundPage = lazy(() => import("@/pages/not-found"));
const LoginPage = lazy(() => import("@/pages/auth/login"));
const RegisterPage = lazy(() => import("@/pages/auth/register"));
const GlobalErrorPage = lazy(() => import("@/pages/global-error"));
import { ProtectedRoute } from "@/components/ProtectedRoute";

function SuspenseWrapper({ children }: { children: React.ReactNode }) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    ref.current?.focus({ preventScroll: true });
  }, []);

  return (
    <div ref={ref} tabIndex={-1} className="animate-page-in outline-none">
      <Suspense fallback={<LoadingState message="Loading page..." />}>
        {children}
      </Suspense>
    </div>
  );
}

export const router = createBrowserRouter([
  {
    path: "/login",
    element: (
      <SuspenseWrapper>
        <LoginPage />
      </SuspenseWrapper>
    ),
  },
  {
    path: "/register",
    element: (
      <SuspenseWrapper>
        <RegisterPage />
      </SuspenseWrapper>
    ),
  },
  {
    path: "/",
    element: (
      <ProtectedRoute>
        <RootLayout />
      </ProtectedRoute>
    ),
    errorElement: (
      <ErrorBoundary>
        <GlobalErrorPage />
      </ErrorBoundary>
    ),
    children: [
      {
        index: true,
        element: (
          <SuspenseWrapper>
            <DashboardPage />
          </SuspenseWrapper>
        ),
      },
      {
        path: "upload",
        element: (
          <SuspenseWrapper>
            <UploadPage />
          </SuspenseWrapper>
        ),
      },
      {
        path: "jobs",
        element: (
          <SuspenseWrapper>
            <JobsPage />
          </SuspenseWrapper>
        ),
      },
      {
        path: "jobs/:id",
        element: (
          <SuspenseWrapper>
            <JobDetailPage />
          </SuspenseWrapper>
        ),
      },
      {
        path: "reports",
        element: (
          <SuspenseWrapper>
            <ReportsPage />
          </SuspenseWrapper>
        ),
      },
      {
        path: "settings",
        element: (
          <SuspenseWrapper>
            <SettingsPage />
          </SuspenseWrapper>
        ),
      },
      {
        path: "*",
        element: (
          <SuspenseWrapper>
            <NotFoundPage />
          </SuspenseWrapper>
        ),
      },
    ],
  },
]);
