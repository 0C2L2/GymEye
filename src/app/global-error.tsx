"use client";

import { useEffect } from "react";

type GlobalErrorPageProps = {
  error?: Error & { digest?: string };
  reset: () => void;
};

export default function GlobalErrorPage({
  error,
  reset
}: GlobalErrorPageProps) {
  useEffect(() => {
    if (error) {
      console.error(error);
    }
  }, [error]);

  const message =
    typeof error?.message === "string" && error.message.trim().length > 0
      ? error.message
      : "A global rendering error occurred.";

  return (
    <html lang="en">
      <body className="bg-ink text-slate-100 antialiased">
        <main className="flex min-h-screen items-center justify-center px-4">
          <section className="w-full max-w-xl rounded-[2rem] border border-white/10 bg-slate-900/90 p-8 text-center shadow-[0_24px_80px_rgba(5,12,24,0.45)]">
            <span className="text-xs uppercase tracking-[0.35em] text-slate-400">
              Application error
            </span>
            <h1 className="mt-4 text-3xl font-semibold text-white">
              Gym Eye could not render this page
            </h1>
            <p className="mt-4 text-sm leading-7 text-slate-300">
              {message}
            </p>
            <button
              type="button"
              onClick={reset}
              className="mt-6 inline-flex items-center justify-center rounded-full bg-gradient-to-r from-cyan-400 to-emerald-400 px-6 py-3 text-sm font-semibold text-slate-950"
            >
              Reload page
            </button>
          </section>
        </main>
      </body>
    </html>
  );
}
