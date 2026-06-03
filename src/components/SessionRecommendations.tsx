type SessionRecommendationsProps = {
  title: string;
  items: string[];
};

export function SessionRecommendations({
  title,
  items
}: SessionRecommendationsProps) {
  return (
    <section className="panel p-6">
      <p className="text-xs uppercase tracking-[0.35em] text-slate-400">
        {title}
      </p>
      <div className="mt-6 grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
        {items.map((item) => (
          <article
            key={item}
            className="rounded-[24px] border border-white/10 bg-slate-950/60 p-4 text-sm leading-7 text-slate-200"
          >
            {item}
          </article>
        ))}
      </div>
    </section>
  );
}
