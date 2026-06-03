export function HeroSection() {
  return (
    <section className="relative overflow-hidden rounded-[32px] border border-white/10 bg-slate-950/70 px-6 py-14 shadow-glow sm:px-10 lg:px-14">
      <div className="absolute inset-0 bg-hero-grid bg-[size:36px_36px] opacity-20" />
      <div className="absolute -left-24 top-10 h-64 w-64 rounded-full bg-cyan-400/15 blur-3xl" />
      <div className="absolute -right-24 bottom-0 h-72 w-72 rounded-full bg-emerald-400/15 blur-3xl" />

      <div className="relative grid gap-10 lg:grid-cols-[1.2fr_0.8fr] lg:items-end">
        <div className="space-y-6">
          <span className="inline-flex rounded-full border border-cyan-400/30 bg-cyan-400/10 px-4 py-2 text-xs font-medium uppercase tracking-[0.32em] text-cyan-100">
            AI-Powered Exercise Form Assistant
          </span>
          <div className="space-y-4">
            <h1 className="max-w-3xl text-5xl font-semibold tracking-tight text-white sm:text-6xl">
              Gym Eye
            </h1>
            <p className="max-w-2xl text-lg leading-8 text-slate-300 sm:text-xl">
              Gym Eye helps users train smarter by watching exercise movement,
              counting reps, detecting form mistakes, and giving real-time
              correction feedback.
            </p>
          </div>
          <div className="flex flex-col gap-3 sm:flex-row">
            <a
              href="/camera"
              className="inline-flex items-center justify-center rounded-full bg-gradient-to-r from-cyan-400 to-emerald-400 px-6 py-3 text-sm font-semibold text-slate-950 transition hover:scale-[1.02]"
            >
              Start Camera Check
            </a>
            <a
              href="/camera"
              className="inline-flex items-center justify-center rounded-full border border-white/15 bg-white/5 px-6 py-3 text-sm font-semibold text-slate-100 transition hover:bg-white/10"
            >
              View Dashboard Demo
            </a>
          </div>
        </div>

        <div className="panel p-6">
          <p className="text-xs uppercase tracking-[0.35em] text-slate-400">
            Future AI signal
          </p>
          <div className="mt-5 space-y-4">
            {[
              "Camera feed enters the browser preview stage.",
              "Raspberry Pi AI classifies exercise and posture faults.",
              "Gym Eye surfaces corrections through a clean coaching panel."
            ].map((item, index) => (
              <div key={item} className="flex gap-4">
                <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-2xl border border-cyan-400/20 bg-cyan-400/10 text-sm font-semibold text-cyan-200">
                  0{index + 1}
                </span>
                <p className="pt-1 text-sm leading-7 text-slate-300">{item}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
