import { ExerciseCard } from "@/components/ExerciseCard";
import { formatConfidence } from "@/lib/formatters";
import type { ExerciseDetectionResult } from "@/types/detection";

type CurrentExercisePanelProps = {
  data: ExerciseDetectionResult;
};

const comingSoonExercises = [
  "Push-up",
  "Deadlift",
  "Shoulder Press",
  "Bicep Curl",
  "Plank"
];

export function CurrentExercisePanel({ data }: CurrentExercisePanelProps) {
  return (
    <section className="panel p-6">
      <div className="flex items-end justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.35em] text-slate-400">
            Current exercise
          </p>
          <h2 className="mt-3 text-2xl font-semibold text-white">
            {data.exercise ?? "Not detected yet"}
          </h2>
        </div>
        <span className="rounded-full border border-cyan-400/20 bg-cyan-400/10 px-3 py-1 text-xs font-medium uppercase tracking-[0.22em] text-cyan-100">
          {formatConfidence(data.confidence)}
        </span>
      </div>

      <div className="mt-4 rounded-[28px] border border-cyan-400/20 bg-cyan-400/10 p-5">
        <div className="grid gap-3 sm:grid-cols-2">
          <div>
            <p className="text-xs uppercase tracking-[0.28em] text-cyan-100/75">
              Category
            </p>
            <p className="mt-2 text-sm text-white">{data.exerciseCategory}</p>
          </div>
          <div>
            <p className="text-xs uppercase tracking-[0.28em] text-cyan-100/75">
              Difficulty
            </p>
            <p className="mt-2 text-sm text-white">{data.difficulty}</p>
          </div>
          <div className="sm:col-span-2">
            <p className="text-xs uppercase tracking-[0.28em] text-cyan-100/75">
              Muscles involved
            </p>
            <p className="mt-2 text-sm text-white">
              {data.musclesInvolved.join(", ")}
            </p>
          </div>
          <div>
            <p className="text-xs uppercase tracking-[0.28em] text-cyan-100/75">
              Live confidence
            </p>
            <p className="mt-2 text-sm text-white">
              {formatConfidence(data.confidence)}
            </p>
          </div>
        </div>
      </div>

      <div className="mt-6">
        <h3 className="text-sm font-semibold uppercase tracking-[0.28em] text-slate-400">
          Upcoming modes
        </h3>
        <div className="mt-4 grid gap-3 sm:grid-cols-2">
          {comingSoonExercises.map((title) => (
            <ExerciseCard key={title} title={title} />
          ))}
        </div>
      </div>
    </section>
  );
}
