import React from "react";
import ReactDOM from "react-dom/client";
import "./styles.css";

function App() {
  return (
    <main className="min-h-screen bg-slate-50 text-slate-950">
      <section className="mx-auto flex min-h-screen max-w-5xl flex-col justify-center px-6 py-12">
        <p className="text-sm font-medium uppercase tracking-wide text-emerald-700">TradeFlow</p>
        <h1 className="mt-3 text-4xl font-semibold">Excel trade data processing</h1>
        <p className="mt-4 max-w-2xl text-base leading-7 text-slate-700">
          Upload, clean, classify, and export shipment data through configurable templates.
        </p>
      </section>
    </main>
  );
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);

