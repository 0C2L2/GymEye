import {
  formatNullableNumber
} from "@/lib/formatters";
import type { RaspberryPiConnectionStatus } from "@/types/raspberryPi";

type RaspberryPiStatusProps = {
  status: RaspberryPiConnectionStatus;
};

export function RaspberryPiStatus({ status }: RaspberryPiStatusProps) {
  return (
    <section className="panel p-6">
      <div className="flex items-end justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.35em] text-slate-400">
            Raspberry Pi status
          </p>
          <h2 className="mt-3 text-2xl font-semibold text-white">
            AI engine connection
          </h2>
        </div>
        <span
          className={`rounded-full border px-3 py-1 text-xs font-medium uppercase tracking-[0.22em] ${
            status.connected
              ? "border-emerald-400/20 bg-emerald-400/10 text-emerald-100"
              : "border-amber-400/20 bg-amber-400/10 text-amber-100"
          }`}
        >
          {status.connected ? "Connected" : "Waiting"}
        </span>
      </div>

      <div className="mt-6 grid gap-3 sm:grid-cols-2">
        <div className="rounded-3xl border border-white/10 bg-slate-950/60 p-4">
          <p className="text-xs uppercase tracking-[0.28em] text-slate-400">AI Engine</p>
          <p className="mt-2 text-sm text-white">
            {status.mode === "demo" ? "Browser Demo Mode" : "Raspberry Pi AI"}
          </p>
        </div>
        <div className="rounded-3xl border border-white/10 bg-slate-950/60 p-4">
          <p className="text-xs uppercase tracking-[0.28em] text-slate-400">Raspberry Pi</p>
          <p className="mt-2 text-sm text-white">
            {status.connected ? "Connected" : "Not Connected"}
          </p>
        </div>
        <div className="rounded-3xl border border-white/10 bg-slate-950/60 p-4">
          <p className="text-xs uppercase tracking-[0.28em] text-slate-400">Latency</p>
          <p className="mt-2 text-sm text-white">{formatNullableNumber(status.latencyMs, " ms")}</p>
        </div>
        <div className="rounded-3xl border border-white/10 bg-slate-950/60 p-4">
          <p className="text-xs uppercase tracking-[0.28em] text-slate-400">FPS</p>
          <p className="mt-2 text-sm text-white">{formatNullableNumber(status.fps)}</p>
        </div>
        <div className="rounded-3xl border border-white/10 bg-slate-950/60 p-4">
          <p className="text-xs uppercase tracking-[0.28em] text-slate-400">Model</p>
          <p className="mt-2 text-sm text-white">{status.modelName ?? "—"}</p>
        </div>
        <div className="rounded-3xl border border-white/10 bg-slate-950/60 p-4">
          <p className="text-xs uppercase tracking-[0.28em] text-slate-400">Last signal</p>
          <p className="mt-2 text-sm text-white">{status.lastSignalAt ?? "No live AI data yet"}</p>
        </div>
      </div>

      <div className="mt-4 rounded-[24px] border border-cyan-400/20 bg-cyan-400/10 p-4 text-sm leading-7 text-cyan-50">
        {status.message}
      </div>
    </section>
  );
}
