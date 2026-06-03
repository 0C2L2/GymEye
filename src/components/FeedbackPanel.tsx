type FeedbackPanelProps = {
  suggestions: string[];
  activeSuggestion: string | null;
};

export function FeedbackPanel({
  suggestions,
  activeSuggestion
}: FeedbackPanelProps) {
  const visibleSuggestions = suggestions.slice(0, 4);

  return (
    <aside className="panel flex flex-col self-start p-6">
      <div className="flex items-end justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.35em] text-slate-400">
            Live feedback
          </p>
          <h2 className="mt-3 text-2xl font-semibold text-white">
            Coaching guidance
          </h2>
        </div>
        {activeSuggestion ? (
          <span className="rounded-full border border-cyan-400/20 bg-cyan-400/10 px-3 py-1 text-xs font-medium uppercase tracking-[0.22em] text-cyan-100">
            Active cue
          </span>
        ) : null}
      </div>

      <div className="mt-4 rounded-[24px] border border-cyan-400/20 bg-cyan-400/10 p-4">
        <p className="text-xs uppercase tracking-[0.28em] text-cyan-100/75">
          Current feedback
        </p>
        <p className="mt-2 text-base font-medium text-white">
          {activeSuggestion ?? "No major mistake detected. Keep going."}
        </p>
      </div>

      <div className="mt-5">
        <p className="text-xs uppercase tracking-[0.35em] text-slate-400">
          Suggested cues
        </p>
      </div>

      <div className="mt-3 grid gap-3">
        {visibleSuggestions.map((suggestion) => (
          <div
            key={suggestion}
            className={`rounded-3xl border px-4 py-3 text-sm ${
              suggestion === activeSuggestion
                ? "border-cyan-400/25 bg-cyan-400/12 text-cyan-50 shadow-glow"
                : "border-white/10 bg-white/[0.04] text-slate-200"
            }`}
          >
            {suggestion}
          </div>
        ))}
      </div>
    </aside>
  );
}
