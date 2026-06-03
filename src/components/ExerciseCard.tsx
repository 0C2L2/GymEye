type ExerciseCardProps = {
  title: string;
};

export function ExerciseCard({ title }: ExerciseCardProps) {
  return (
    <article className="rounded-3xl border border-white/10 bg-slate-900/70 p-4">
      <div className="flex items-center justify-between gap-3">
        <h4 className="text-sm font-semibold text-white">{title}</h4>
        <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-slate-300">
          Coming soon
        </span>
      </div>
    </article>
  );
}
