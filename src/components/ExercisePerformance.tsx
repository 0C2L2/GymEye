const exercises = [
  { name: "Squat", score: 84 },
  { name: "Push-up", score: 79 },
  { name: "Deadlift", score: 76 },
  { name: "Shoulder Press", score: 82 }
];

export function ExercisePerformance() {
  return (
    <section className="panel p-6">
      <p className="text-xs uppercase tracking-[0.35em] text-slate-400">
        Exercise performance
      </p>
      <div className="mt-6 space-y-4">
        {exercises.map((exercise) => (
          <div key={exercise.name}>
            <div className="flex items-center justify-between text-sm text-slate-300">
              <span>{exercise.name}</span>
              <span>{exercise.score}% average form</span>
            </div>
            <div className="mt-2 h-2 overflow-hidden rounded-full bg-white/10">
              <div
                className="h-full rounded-full bg-gradient-to-r from-cyan-400 to-emerald-400"
                style={{ width: `${exercise.score}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
