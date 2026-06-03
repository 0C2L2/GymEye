type ExerciseProgressProps = {
  value: number;
};

export function ExerciseProgress({ value }: ExerciseProgressProps) {
  return (
    <div>
      <div className="h-3 overflow-hidden rounded-full bg-white/10">
        <div
          className="h-full rounded-full bg-gradient-to-r from-cyan-400 via-sky-400 to-emerald-400"
          style={{ width: `${value}%` }}
        />
      </div>
      <p className="mt-3 text-sm text-slate-300">{value}% set complete</p>
    </div>
  );
}
