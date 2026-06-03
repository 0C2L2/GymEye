import type { SessionTimelineEvent } from "@/types/detection";

type SessionTimelineProps = {
  events: SessionTimelineEvent[];
};

export function SessionTimeline({ events }: SessionTimelineProps) {
  return (
    <section className="panel p-6">
      <p className="text-xs uppercase tracking-[0.35em] text-slate-400">
        Session timeline
      </p>
      <div className="mt-6 space-y-4">
        {events.map((item, index) => (
          <div key={`${item.time}-${index}`} className="flex gap-4">
            <div className="flex flex-col items-center">
              <span className="h-3 w-3 rounded-full bg-cyan-300" />
              {index < events.length - 1 ? (
                <span className="mt-2 h-full w-px bg-white/10" />
              ) : null}
            </div>
            <div className="pb-4">
              <p className="text-sm font-medium text-cyan-100">{item.time}</p>
              <p className="mt-1 text-sm text-slate-300">{item.event}</p>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
