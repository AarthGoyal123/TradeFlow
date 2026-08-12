import path from "path";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";
const apiBaseUrl = process.env.VITE_API_BASE_URL || "http://localhost:8000";
export default defineConfig({
    plugins: [react()],
    resolve: {
        alias: {
            "@": path.resolve(__dirname, "./src"),
        },
    },
    server: {
        port: 5173,
        proxy: {
            "/api": {
                target: apiBaseUrl,
                changeOrigin: true,
                rewrite: (p) => p.replace(/^\/api/, ""),
            },
        },
    },
});
