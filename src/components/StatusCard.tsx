type StatusTone = "good" | "neutral" | "warn";

type StatusCardProps = {
  label: string;
  value: string;
  tone?: StatusTone;
};

const toneClasses: Record<StatusTone, string> = {
  good: "border-emerald-400/20 bg-emerald-400/10 text-emerald-200",
  neutral: "border-cyan-400/20 bg-cyan-400/10 text-cyan-100",
  warn: "border-amber-400/20 bg-amber-400/10 text-amber-100"
};

export function StatusCard({
  label,
  value,
  tone = "neutral"
}: StatusCardProps) {
  return (
    <article className="panel p-4">
      <p className="text-xs uppercase tracking-[0.3em] text-slate-400">{label}</p>
      <div
        className={`mt-4 inline-flex rounded-full border px-3 py-2 text-sm font-medium ${toneClasses[tone]}`}
      >
        {value}
      </div>
    </article>
  );
}
