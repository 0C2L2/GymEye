import { StatCard } from "@/components/StatCard";
import {
  formatConfidence,
  formatDuration,
  formatPercent,
  formatRepTime
} from "@/lib/formatters";
import type { ExerciseDetectionResult } from "@/types/detection";

type WorkoutStatsPanelProps = {
  data: ExerciseDetectionResult;
};

export function WorkoutStatsPanel({ data }: WorkoutStatsPanelProps) {
  const remainingReps = Math.max(data.targetReps - data.completedReps, 0);

  const cards = [
    { label: "Current exercise", value: data.exercise ?? "Not detected yet" },
    { label: "Total reps", value: String(data.completedReps) },
    { label: "Correct reps", value: String(data.correctReps) },
    { label: "Incorrect reps", value: String(data.incorrectReps) },
    { label: "Current set", value: String(data.set) },
    { label: "Target reps", value: String(data.targetReps) },
    { label: "Remaining reps", value: String(remainingReps) },
    { label: "Workout duration", value: formatDuration(data.durationSeconds) },
    { label: "Average rep time", value: formatRepTime(data.averageRepTimeSeconds) },
    { label: "Current pace", value: data.currentPace },
    { label: "Estimated calories", value: `${data.caloriesEstimate} kcal` },
    { label: "Form accuracy", value: formatPercent(data.formScore) },
    { label: "AI confidence", value: formatConfidence(data.confidence) },
    {
      label: "Mistakes detected",
      value: String(data.mistakes.reduce((sum, item) => sum + item.count, 0))
    },
    { label: "Last mistake", value: data.mistakes[0]?.label ?? "None" },
    { label: "Best rep score", value: formatPercent(data.bestRepScore) },
    { label: "Worst rep score", value: formatPercent(data.worstRepScore) }
  ];

  return (
    <section className="panel p-6">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.35em] text-slate-400">
            Workout stats dashboard
          </p>
          <h2 className="mt-3 text-2xl font-semibold text-white">
            Session metrics
          </h2>
        </div>
        <p className="max-w-xl text-sm leading-7 text-slate-300">
          These values are demo placeholders now. The layout is structured so
          live Raspberry Pi inference can swap in directly later.
        </p>
      </div>

      <div className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {cards.map((card) => (
          <StatCard key={card.label} {...card} />
        ))}
      </div>
    </section>
  );
}
