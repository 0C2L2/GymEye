import { formatPercent } from "@/lib/formatters";

type FormScoreCardProps = {
  formScore: number;
  scores: {
    balance: number;
    rangeOfMotion: number;
    speedControl: number;
    posture: number;
  };
};

function getFormState(score: number) {
  if (score >= 90) {
    return "Excellent";
  }

  if (score >= 75) {
    return "Good";
  }

  if (score >= 50) {
    return "Needs work";
  }

  return "Poor";
}

export function FormScoreCard({ formScore, scores }: FormScoreCardProps) {
  const metrics = [
    { label: "Balance", value: scores.balance },
    { label: "Range of motion", value: scores.rangeOfMotion },
    { label: "Speed control", value: scores.speedControl },
    { label: "Posture", value: scores.posture }
  ];

  return (
    <section className="panel p-6">
      <p className="text-xs uppercase tracking-[0.35em] text-slate-400">
        Form quality
      </p>
      <div className="mt-4 flex items-end justify-between gap-4">
        <div>
          <p className="text-sm text-slate-300">Form Score</p>
          <p className="mt-2 text-4xl font-semibold text-white">
            {formatPercent(formScore)}
          </p>
        </div>
        <span className="rounded-full border border-cyan-400/20 bg-cyan-400/10 px-4 py-2 text-sm font-medium text-cyan-100">
          {getFormState(formScore)}
        </span>
      </div>

      <div className="mt-6 space-y-3">
        {metrics.map((metric) => (
          <div key={metric.label}>
            <div className="flex items-center justify-between text-sm text-slate-300">
              <span>{metric.label}</span>
              <span>{formatPercent(metric.value)}</span>
            </div>
            <div className="mt-2 h-2 overflow-hidden rounded-full bg-white/10">
              <div
                className="h-full rounded-full bg-gradient-to-r from-cyan-400 to-emerald-400"
                style={{ width: `${metric.value}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
