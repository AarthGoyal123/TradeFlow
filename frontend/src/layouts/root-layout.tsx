import { useState } from "react";
import { Outlet } from "react-router-dom";

import { Header } from "@/layouts/header";
import { Sidebar } from "@/layouts/sidebar";

export function RootLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <div className="flex flex-1 flex-col overflow-hidden">
        <Header onMenuClick={() => setSidebarOpen((prev) => !prev)} />
        <main className="flex-1 overflow-y-auto p-4 md:p-6" aria-label="Main content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
