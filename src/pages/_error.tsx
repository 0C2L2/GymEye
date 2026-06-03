import type { NextPageContext } from "next";

type ErrorPageProps = {
  statusCode?: number;
};

function ErrorPage({ statusCode }: ErrorPageProps) {
  return (
    <main className="flex min-h-screen items-center justify-center bg-ink px-4 text-slate-100">
      <div className="panel max-w-xl p-8 text-center">
        <p className="text-xs uppercase tracking-[0.35em] text-slate-400">
          Request error
        </p>
        <h1 className="mt-4 text-3xl font-semibold text-white">
          {statusCode ? `Error ${statusCode}` : "Unexpected error"}
        </h1>
        <p className="mt-4 text-sm leading-7 text-slate-300">
          Gym Eye could not complete this request.
        </p>
      </div>
    </main>
  );
}

ErrorPage.getInitialProps = ({ res, err }: NextPageContext) => {
  const statusCode = res?.statusCode ?? err?.statusCode ?? 404;

  return { statusCode };
};

export default ErrorPage;
