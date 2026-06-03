import type { ExerciseMistake } from "@/types/detection";

type CommonMistakesProps = {
  mistakes: ExerciseMistake[];
};

export function CommonMistakes({ mistakes }: CommonMistakesProps) {
  return (
    <section className="panel p-6">
      <p className="text-xs uppercase tracking-[0.35em] text-slate-400">
        Common mistakes
      </p>
      <div className="mt-6 space-y-4">
        {mistakes.map((mistake) => (
          <article
            key={mistake.type}
            className="rounded-[24px] border border-white/10 bg-slate-950/60 p-4"
          >
            <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <h3 className="text-lg font-semibold text-white">{mistake.label}</h3>
                <p className="mt-2 text-sm leading-7 text-slate-300">
                  {mistake.suggestion}
                </p>
              </div>
              <div className="flex flex-wrap gap-2">
                <span className="rounded-full border border-white/10 bg-white/[0.04] px-3 py-1 text-xs font-medium text-slate-200">
                  {mistake.count} times
                </span>
                <span className="rounded-full border border-white/10 bg-white/[0.04] px-3 py-1 text-xs font-medium text-slate-200">
                  {mistake.severity}
                </span>
              </div>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
