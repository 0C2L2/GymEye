import { StatCard } from "@/components/StatCard";
import { formatPercent, formatRepTime } from "@/lib/formatters";
import type { WorkoutSessionSummary } from "@/types/session";

type SessionPerformanceOverviewProps = {
  session: WorkoutSessionSummary;
};

export function SessionPerformanceOverview({
  session
}: SessionPerformanceOverviewProps) {
  const repCompletion = Math.round((session.totalReps / session.totalReps) * 100);
  const correctRepRate = Math.round((session.correctReps / session.totalReps) * 100);
  const mistakeRate = Math.round((session.incorrectReps / session.totalReps) * 100);
  const averageRepTime =
    session.repResults.reduce((sum, rep) => sum + rep.durationSeconds, 0) /
    session.repResults.length;

  return (
    <section className="panel p-6">
      <div>
        <p className="text-xs uppercase tracking-[0.35em] text-slate-400">
          Performance Overview
        </p>
        <h2 className="mt-3 text-2xl font-semibold text-white">Session quality</h2>
      </div>
      <div className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        <StatCard label="Average form score" value={formatPercent(session.averageFormScore)} />
        <StatCard label="Rep completion" value={formatPercent(repCompletion)} />
        <StatCard label="Correct rep rate" value={formatPercent(correctRepRate)} />
        <StatCard label="Mistake rate" value={formatPercent(mistakeRate)} />
        <StatCard label="Average rep time" value={formatRepTime(averageRepTime)} />
        <StatCard label="Pace" value="Good" />
      </div>
    </section>
  );
}
