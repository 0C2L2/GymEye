import { ExerciseProgress } from "@/components/ExerciseProgress";

type RepCounterProps = {
  completedReps: number;
  targetReps: number;
  correctReps: number;
  incorrectReps: number;
};

export function RepCounter({
  completedReps,
  targetReps,
  correctReps,
  incorrectReps
}: RepCounterProps) {
  const remaining = Math.max(targetReps - completedReps, 0);
  const progress = Math.min(Math.round((completedReps / targetReps) * 100), 100);

  return (
    <section className="panel p-6">
      <p className="text-xs uppercase tracking-[0.35em] text-slate-400">
        Rep counter
      </p>
      <div className="mt-5 flex items-end justify-between gap-4">
        <div>
          <p className="text-4xl font-semibold text-white sm:text-5xl">
            {completedReps} <span className="text-slate-500">/ {targetReps}</span>
          </p>
          <p className="mt-3 text-sm text-slate-300">reps</p>
        </div>
        <div className="rounded-[24px] border border-cyan-400/20 bg-cyan-400/10 px-4 py-3 text-right">
          <p className="text-xs uppercase tracking-[0.28em] text-cyan-100">
            Set progress
          </p>
          <p className="mt-2 text-2xl font-semibold text-white">{progress}%</p>
        </div>
      </div>

      <div className="mt-6">
        <ExerciseProgress value={progress} />
      </div>

      <div className="mt-6 grid gap-3 sm:grid-cols-3">
        <div className="rounded-3xl border border-emerald-400/20 bg-emerald-400/10 px-4 py-3 text-sm text-emerald-100">
          Correct reps: {correctReps}
        </div>
        <div className="rounded-3xl border border-amber-400/20 bg-amber-400/10 px-4 py-3 text-sm text-amber-100">
          Needs improvement: {incorrectReps}
        </div>
        <div className="rounded-3xl border border-white/10 bg-white/[0.04] px-4 py-3 text-sm text-slate-200">
          Remaining: {remaining}
        </div>
      </div>
    </section>
  );
}
