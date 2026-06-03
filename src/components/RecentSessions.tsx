import { formatDuration, formatPercent } from "@/lib/formatters";
import type { RecentWorkoutSession } from "@/types/session";

type RecentSessionsProps = {
  sessions: RecentWorkoutSession[];
};

export function RecentSessions({ sessions }: RecentSessionsProps) {
  return (
    <section className="panel p-6">
      <div className="flex items-end justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.35em] text-slate-400">
            Recent sessions
          </p>
          <h2 className="mt-3 text-2xl font-semibold text-white">
            Workout history
          </h2>
        </div>
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        {sessions.map((session) => (
          <article
            key={session.id}
            className="rounded-[26px] border border-white/10 bg-slate-950/60 p-5"
          >
            <div className="flex items-start justify-between gap-3">
              <div>
                <h3 className="text-lg font-semibold text-white">{session.exercise}</h3>
                <p className="mt-1 text-sm text-slate-400">{session.dateLabel}</p>
              </div>
              <span className="rounded-full border border-cyan-400/20 bg-cyan-400/10 px-3 py-1 text-xs font-medium text-cyan-100">
                {formatPercent(session.formScore)} form
              </span>
            </div>
            <div className="mt-4 grid gap-3 sm:grid-cols-3 text-sm text-slate-300">
              <p>{session.totalReps} reps</p>
              <p>{session.mistakesCount} mistakes</p>
              <p>{formatDuration(session.durationSeconds)}</p>
            </div>
            <a
              href="/session-summary"
              className="mt-5 inline-flex items-center justify-center rounded-full border border-white/15 bg-white/5 px-4 py-2 text-sm font-semibold text-white"
            >
              View Summary
            </a>
          </article>
        ))}
      </div>
    </section>
  );
}
