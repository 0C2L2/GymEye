import { Header } from "@/components/Header";
import { RaspberryPiStatus } from "@/components/RaspberryPiStatus";
import { RepBreakdown } from "@/components/RepBreakdown";
import { SessionPerformanceOverview } from "@/components/SessionPerformanceOverview";
import { SessionRecommendations } from "@/components/SessionRecommendations";
import { SessionSummaryHeader } from "@/components/SessionSummaryHeader";
import { StatCard } from "@/components/StatCard";
import { getMockRaspberryPiStatus } from "@/lib/mockDetection";
import { formatCalories, formatDuration, formatPercent } from "@/lib/formatters";
import { getMockSessionSummary } from "@/lib/mockSessions";

const goodPoints = [
  "Good depth on most reps",
  "Stable pace through the set",
  "Strong posture improvement after rep 8"
];

const needsImprovement = [
  "Knees moved inward on 2 reps",
  "Back angle dropped during fatigue",
  "Slow down slightly during the lowering phase"
];

const nextSteps = [
  "Focus on knee alignment.",
  "Use a slower controlled descent.",
  "Try 3 sets of 12 reps with 60 seconds rest."
];

export default function SessionSummaryPage() {
  const session = getMockSessionSummary();
  const summaryCards = [
    { label: "Exercise", value: session.exercise },
    { label: "Total reps", value: String(session.totalReps) },
    { label: "Correct reps", value: String(session.correctReps) },
    { label: "Incorrect reps", value: String(session.incorrectReps) },
    { label: "Average form score", value: formatPercent(session.averageFormScore) },
    { label: "Best rep score", value: formatPercent(session.bestRepScore) },
    { label: "Worst rep score", value: formatPercent(session.worstRepScore) },
    {
      label: "Most common mistake",
      value: session.mostCommonMistake ?? "None"
    },
    { label: "Total time", value: formatDuration(session.durationSeconds) },
    { label: "Calories estimate", value: formatCalories(session.caloriesEstimate) }
  ];

  return (
    <main className="min-h-screen">
      <Header />
      <div className="mx-auto flex max-w-7xl flex-col gap-6 px-4 py-8 sm:px-6 lg:px-8 lg:py-10">
        <SessionSummaryHeader exercise={session.exercise} />

        <section className="panel p-6">
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
            {summaryCards.map((card) => (
              <StatCard key={card.label} {...card} />
            ))}
          </div>
        </section>

        <SessionPerformanceOverview session={session} />

        <section className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
          <RepBreakdown reps={session.repResults} />
          <RaspberryPiStatus status={getMockRaspberryPiStatus()} />
        </section>

        <SessionRecommendations title="What Went Well" items={goodPoints} />
        <SessionRecommendations title="Needs Improvement" items={needsImprovement} />
        <SessionRecommendations
          title="Recommended for next session"
          items={nextSteps}
        />
      </div>
    </main>
  );
}
