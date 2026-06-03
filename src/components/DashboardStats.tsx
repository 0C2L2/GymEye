import { StatCard } from "@/components/StatCard";

export function DashboardStats() {
  const stats = [
    { label: "Total sessions", value: "8" },
    { label: "Total reps", value: "420" },
    { label: "Average form score", value: "81%" },
    { label: "Correct reps", value: "336" },
    { label: "Incorrect reps", value: "84" },
    { label: "Most trained exercise", value: "Squat" },
    { label: "Most common mistake", value: "Back not straight" },
    { label: "Improvement this week", value: "+12%" }
  ];

  return (
    <section className="panel p-6">
      <div>
        <p className="text-xs uppercase tracking-[0.35em] text-slate-400">
          Dashboard
        </p>
        <h2 className="mt-3 text-2xl font-semibold text-white">Training overview</h2>
      </div>
      <div className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {stats.map((stat) => (
          <StatCard key={stat.label} {...stat} />
        ))}
      </div>
    </section>
  );
}
