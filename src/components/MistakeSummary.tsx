import type { ExerciseMistake } from "@/types/detection";

type MistakeSummaryProps = {
  mistakes: ExerciseMistake[];
};

const severityClasses = {
  low: "border-sky-400/20 bg-sky-400/10 text-sky-100",
  medium: "border-amber-400/20 bg-amber-400/10 text-amber-100",
  high: "border-rose-400/20 bg-rose-400/10 text-rose-100"
};

export function MistakeSummary({ mistakes }: MistakeSummaryProps) {
  return (
    <section className="panel p-6">
      <div className="flex items-end justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.35em] text-slate-400">
            Mistake tracking
          </p>
          <h2 className="mt-3 text-2xl font-semibold text-white">
            Movement issues detected
          </h2>
        </div>
        <p className="text-sm text-slate-400">{mistakes.length} issue types</p>
      </div>

      <div className="mt-6 space-y-4">
        {mistakes.map((mistake) => (
          <article
            key={mistake.type}
            className="rounded-[26px] border border-white/10 bg-slate-950/60 p-4"
          >
            <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <h3 className="text-lg font-semibold text-white">{mistake.label}</h3>
                <p className="mt-2 text-sm leading-7 text-slate-300">
                  {mistake.suggestion}
                </p>
              </div>
              <div className="flex flex-wrap gap-2">
                <span
                  className={`rounded-full border px-3 py-1 text-xs font-medium uppercase tracking-[0.25em] ${severityClasses[mistake.severity]}`}
                >
                  {mistake.severity}
                </span>
                <span className="rounded-full border border-white/10 bg-white/[0.04] px-3 py-1 text-xs font-medium uppercase tracking-[0.25em] text-slate-200">
                  Count {mistake.count}
                </span>
              </div>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
