type SessionSummaryHeaderProps = {
  exercise: string;
};

export function SessionSummaryHeader({ exercise }: SessionSummaryHeaderProps) {
  return (
    <section className="panel px-6 py-8 sm:px-8">
      <p className="text-xs uppercase tracking-[0.35em] text-slate-400">
        Workout Complete
      </p>
      <h1 className="mt-3 text-4xl font-semibold tracking-tight text-white">
        {exercise} Session Summary
      </h1>
      <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-300">
        Great work. Your form score improved compared to your previous session.
      </p>
      <div className="mt-6 flex flex-col gap-3 sm:flex-row">
        <a
          href="/camera"
          className="inline-flex items-center justify-center rounded-full bg-gradient-to-r from-cyan-400 to-emerald-400 px-6 py-3 text-sm font-semibold text-slate-950"
        >
          Start New Session
        </a>
        <a
          href="/dashboard"
          className="inline-flex items-center justify-center rounded-full border border-white/15 bg-white/5 px-6 py-3 text-sm font-semibold text-white"
        >
          View Dashboard
        </a>
        <a
          href="/camera"
          className="inline-flex items-center justify-center rounded-full border border-white/15 bg-white/5 px-6 py-3 text-sm font-semibold text-white"
        >
          Back to Camera
        </a>
      </div>
    </section>
  );
}
