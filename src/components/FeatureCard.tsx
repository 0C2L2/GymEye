type FeatureCardProps = {
  title: string;
  description: string;
};

export function FeatureCard({ title, description }: FeatureCardProps) {
  return (
    <article className="panel p-6 transition hover:-translate-y-1 hover:border-cyan-400/30 hover:bg-white/[0.07]">
      <div className="mb-4 h-1.5 w-16 rounded-full bg-gradient-to-r from-cyan-400 to-emerald-400" />
      <h3 className="text-xl font-semibold text-white">{title}</h3>
      <p className="mt-3 text-sm leading-7 text-slate-300">{description}</p>
    </article>
  );
}
