import { FeatureCard } from "@/components/FeatureCard";
import { Header } from "@/components/Header";
import { HeroSection } from "@/components/HeroSection";

const features = [
  {
    title: "Real-time camera analysis",
    description:
      "A future-ready camera interface built for presence checks, exercise detection, and live movement visibility."
  },
  {
    title: "Rep counting",
    description:
      "Session scaffolding already supports completed reps, remaining reps, sets, pace, and timing metrics."
  },
  {
    title: "Form mistake detection",
    description:
      "Clean mistake summaries are ready for severity, counts, and targeted exercise correction suggestions."
  },
  {
    title: "Exercise stats dashboard",
    description:
      "A polished dashboard layout shows exercise status, form quality, confidence, and performance trends."
  },
  {
    title: "Correction suggestions",
    description:
      "Live coaching cues stay visible in a dedicated panel so users can react during each set."
  },
  {
    title: "Raspberry Pi AI integration ready",
    description:
      "Browser-side placeholders are isolated from UI rendering so real Raspberry Pi payloads can replace them cleanly."
  }
];

const workflow = [
  "User starts camera",
  "Gym Eye detects the person",
  "Exercise is recognized",
  "Reps and movement quality are tracked",
  "Mistakes are shown",
  "Correct technique suggestions are displayed"
];

export default function HomePage() {
  return (
    <main className="min-h-screen">
      <Header />
      <div className="mx-auto flex max-w-7xl flex-col gap-10 px-4 py-8 sm:px-6 lg:px-8 lg:py-12">
        <HeroSection />

        <section className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
          {features.map((feature) => (
            <FeatureCard key={feature.title} {...feature} />
          ))}
        </section>

        <section id="workflow" className="panel px-6 py-8 sm:px-8 sm:py-10">
          <div className="max-w-3xl">
            <p className="text-xs uppercase tracking-[0.35em] text-slate-400">
              Future workflow
            </p>
            <h2 className="mt-3 text-3xl font-semibold text-white">
              How the full Gym Eye loop will work
            </h2>
            <p className="mt-3 text-sm leading-7 text-slate-300">
              This frontend prototype focuses on camera access, visibility checks,
              and a polished coaching dashboard. Later, the Raspberry Pi AI layer
              will supply exercise recognition and form correction signals.
            </p>
          </div>

          <div className="mt-8 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {workflow.map((item, index) => (
              <article
                key={item}
                className="rounded-[28px] border border-white/10 bg-slate-950/60 p-5"
              >
                <span className="inline-flex h-10 w-10 items-center justify-center rounded-2xl border border-cyan-400/20 bg-cyan-400/10 text-sm font-semibold text-cyan-100">
                  0{index + 1}
                </span>
                <p className="mt-4 text-lg font-medium text-white">{item}</p>
              </article>
            ))}
          </div>
        </section>
      </div>
    </main>
  );
}
