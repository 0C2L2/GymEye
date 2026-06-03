import { CommonMistakes } from "@/components/CommonMistakes";
import { DashboardStats } from "@/components/DashboardStats";
import { ExercisePerformance } from "@/components/ExercisePerformance";
import { Header } from "@/components/Header";
import { RaspberryPiStatus } from "@/components/RaspberryPiStatus";
import { RecentSessions } from "@/components/RecentSessions";
import { StatCard } from "@/components/StatCard";
import {
  getMockConnectedRaspberryPiStatus
} from "@/lib/mockDetection";
import { getMockCommonMistakes, getMockRecentSessions } from "@/lib/mockSessions";

const progressCards = [
  { label: "Weekly reps", value: "128", helper: "Up from 96 last week" },
  { label: "Average form score", value: "81%", helper: "Trending upward" },
  { label: "Mistakes reduced", value: "-18%", helper: "Compared to last week" },
  { label: "Best exercise", value: "Squat", helper: "84% average form" },
  { label: "Needs most improvement", value: "Deadlift", helper: "76% average form" }
];

export default function DashboardPage() {
  return (
    <main className="min-h-screen">
      <Header />
      <div className="mx-auto flex max-w-7xl flex-col gap-6 px-4 py-8 sm:px-6 lg:px-8 lg:py-10">
        <section className="panel px-6 py-8 sm:px-8">
          <p className="text-xs uppercase tracking-[0.35em] text-slate-400">
            Dashboard
          </p>
          <h1 className="mt-3 text-4xl font-semibold tracking-tight text-white">
            Workout history and progress
          </h1>
          <p className="mt-3 max-w-3xl text-sm leading-7 text-slate-300">
            This page uses mock session history now, but the layout is prepared
            for live workout storage and Raspberry Pi AI trends later.
          </p>
        </section>

        <DashboardStats />

        <section className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
          <RecentSessions sessions={getMockRecentSessions()} />
          <RaspberryPiStatus status={getMockConnectedRaspberryPiStatus()} />
        </section>

        <section className="panel p-6">
          <p className="text-xs uppercase tracking-[0.35em] text-slate-400">
            Progress overview
          </p>
          <div className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
            {progressCards.map((card) => (
              <StatCard key={card.label} {...card} />
            ))}
          </div>
        </section>

        <section className="grid gap-6 xl:grid-cols-[0.9fr_1.1fr]">
          <ExercisePerformance />
          <CommonMistakes mistakes={getMockCommonMistakes()} />
        </section>
      </div>
    </main>
  );
}
