import { formatRepTime } from "@/lib/formatters";
import type { RepResult, RepStatus } from "@/types/session";

type RepBreakdownProps = {
  reps: RepResult[];
  compact?: boolean;
  title?: string;
};

const statusTone: Record<RepStatus, string> = {
  excellent: "border-emerald-400/20 bg-emerald-400/10 text-emerald-100",
  good: "border-cyan-400/20 bg-cyan-400/10 text-cyan-100",
  needs_work: "border-amber-400/20 bg-amber-400/10 text-amber-100",
  poor: "border-rose-400/20 bg-rose-400/10 text-rose-100"
};

function getStatusLabel(status: RepStatus) {
  switch (status) {
    case "needs_work":
      return "Needs work";
    default:
      return status.charAt(0).toUpperCase() + status.slice(1);
  }
}

export function RepBreakdown({
  reps,
  compact = false,
  title = "Rep-by-rep breakdown"
}: RepBreakdownProps) {
  return (
    <section className="panel p-6">
      <div className="flex items-end justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.35em] text-slate-400">
            {title}
          </p>
          <h2 className="mt-3 text-2xl font-semibold text-white">Rep analysis</h2>
        </div>
        <p className="text-sm text-slate-400">{reps.length} reps</p>
      </div>

      <div className="mt-6 hidden lg:block">
        <div className="overflow-hidden rounded-[24px] border border-white/10">
          <table className="min-w-full border-collapse">
            <thead className="bg-white/[0.04] text-left text-xs uppercase tracking-[0.28em] text-slate-400">
              <tr>
                <th className="px-4 py-3">Rep</th>
                <th className="px-4 py-3">Score</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Mistake</th>
                <th className="px-4 py-3">Duration</th>
                <th className="px-4 py-3">Correct</th>
              </tr>
            </thead>
            <tbody>
              {reps.map((rep) => (
                <tr key={rep.repNumber} className="border-t border-white/10 bg-slate-950/50">
                  <td className="px-4 py-4 text-sm text-white">Rep {rep.repNumber}</td>
                  <td className="px-4 py-4 text-sm text-white">{rep.score}%</td>
                  <td className="px-4 py-4">
                    <span
                      className={`rounded-full border px-3 py-1 text-xs font-medium uppercase tracking-[0.2em] ${statusTone[rep.status]}`}
                    >
                      {getStatusLabel(rep.status)}
                    </span>
                  </td>
                  <td className="px-4 py-4 text-sm text-slate-300">
                    {rep.mistake ?? "None"}
                  </td>
                  <td className="px-4 py-4 text-sm text-slate-300">
                    {formatRepTime(rep.durationSeconds)}
                  </td>
                  <td className="px-4 py-4 text-sm text-slate-300">
                    {rep.correct ? "Correct" : "Incorrect"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className={`mt-6 grid gap-3 ${compact ? "grid-cols-1" : "grid-cols-1 sm:grid-cols-2"} lg:hidden`}>
        {reps.map((rep) => (
          <article
            key={rep.repNumber}
            className="rounded-[24px] border border-white/10 bg-slate-950/60 p-4"
          >
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="text-base font-semibold text-white">
                  Rep {rep.repNumber} - {rep.score}%
                </p>
                <p className="mt-1 text-sm text-slate-300">
                  {rep.mistake ?? getStatusLabel(rep.status)}
                </p>
              </div>
              <span
                className={`rounded-full border px-3 py-1 text-xs font-medium uppercase tracking-[0.2em] ${statusTone[rep.status]}`}
              >
                {getStatusLabel(rep.status)}
              </span>
            </div>
            <div className="mt-4 flex flex-wrap gap-2 text-xs text-slate-300">
              <span className="rounded-full border border-white/10 bg-white/[0.04] px-3 py-1">
                {formatRepTime(rep.durationSeconds)}
              </span>
              <span className="rounded-full border border-white/10 bg-white/[0.04] px-3 py-1">
                {rep.correct ? "Correct" : "Incorrect"}
              </span>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
