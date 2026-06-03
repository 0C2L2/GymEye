import type { ExerciseDetectionResult } from "@/types/detection";

type DebugPayloadPanelProps = {
  payload: ExerciseDetectionResult;
};

export function DebugPayloadPanel({ payload }: DebugPayloadPanelProps) {
  const compactPayload = {
    cameraActive: payload.cameraActive,
    exercise: payload.exercise,
    completedReps: payload.completedReps,
    correctReps: payload.correctReps,
    incorrectReps: payload.incorrectReps,
    formScore: payload.formScore,
    confidence: payload.confidence,
    activeSuggestion: payload.activeSuggestion,
    mistakes: payload.mistakes,
    raspberryPiStatus: payload.raspberryPiStatus
  };

  return (
    <section className="panel px-6 py-6 sm:px-8">
      <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.35em] text-slate-400">
            Future Raspberry Pi AI payload
          </p>
          <h2 className="mt-3 text-2xl font-semibold text-white">
            Developer debug structure
          </h2>
        </div>
        <p className="max-w-md text-sm text-slate-300">
          Compact preview of the payload shape for future live integration.
        </p>
      </div>

      <pre className="mt-5 max-h-[420px] overflow-auto rounded-[28px] border border-white/10 bg-slate-950/80 p-4 text-xs leading-6 text-cyan-100">
        {JSON.stringify(compactPayload, null, 2)}
      </pre>
    </section>
  );
}
