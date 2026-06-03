"use client";

import { useMemo, useState } from "react";

import { CameraPreview } from "@/components/CameraPreview";
import { CurrentExercisePanel } from "@/components/CurrentExercisePanel";
import { DebugPayloadPanel } from "@/components/DebugPayloadPanel";
import { FeedbackPanel } from "@/components/FeedbackPanel";
import { FormScoreCard } from "@/components/FormScoreCard";
import { Header } from "@/components/Header";
import { MistakeSummary } from "@/components/MistakeSummary";
import { RaspberryPiStatus } from "@/components/RaspberryPiStatus";
import { RepBreakdown } from "@/components/RepBreakdown";
import { RepCounter } from "@/components/RepCounter";
import { SessionTimeline } from "@/components/SessionTimeline";
import { StatusCard } from "@/components/StatusCard";
import { WorkoutStatsPanel } from "@/components/WorkoutStatsPanel";
import {
  futurePayloadExample,
  getIdleSuggestions,
  getMockDetectionResult
} from "@/lib/mockDetection";
import type { ExerciseDetectionResult } from "@/types/detection";

export default function CameraPage() {
  const [cameraActive, setCameraActive] = useState(false);
  const [detection, setDetection] = useState<ExerciseDetectionResult | null>(null);

  const activeData = detection ?? getMockDetectionResult();
  const isChecking = cameraActive && detection === null;

  const statusCards = useMemo(
    () => [
      {
        label: "Camera",
        value: cameraActive ? "Active" : "Inactive",
        tone: cameraActive ? "good" : "warn"
      },
      {
        label: "Person detected",
        value:
          !cameraActive
            ? "No"
            : isChecking
              ? "Checking..."
              : activeData.personDetected
                ? "Yes"
                : "No",
        tone:
          !cameraActive || (!isChecking && !activeData.personDetected)
            ? "warn"
            : "good"
      },
      {
        label: "Face detected",
        value:
          !cameraActive
            ? "No"
            : isChecking
              ? "Checking..."
              : activeData.faceDetected
                ? "Yes"
                : "No",
        tone:
          !cameraActive || (!isChecking && !activeData.faceDetected)
            ? "warn"
            : "good"
      },
      {
        label: "Body visible",
        value: !cameraActive ? "Not detected" : isChecking ? "Checking..." : activeData.bodyVisible === "full" ? "Full" : activeData.bodyVisible === "partial" ? "Partial" : "Not detected",
        tone: cameraActive && !isChecking && activeData.bodyVisible === "full" ? "good" : "neutral"
      },
      {
        label: "AI source",
        value: activeData.source,
        tone: "neutral"
      },
      {
        label: "Raspberry Pi connection",
        value: activeData.raspberryPiStatus.connected ? "Connected" : "Not connected",
        tone: "neutral"
      }
    ],
    [activeData, cameraActive, isChecking]
  );

  const feedbackSuggestions = cameraActive
    ? activeData.activeFeedback
    : getIdleSuggestions();

  const mobileFeedbackHeadline = cameraActive
    ? activeData.activeSuggestion ?? "No major mistake detected. Keep going."
    : "Stand fully inside the camera frame.";

  return (
    <main className="min-h-screen">
      <Header />
      <div className="mx-auto flex max-w-7xl flex-col gap-6 px-4 py-8 sm:px-6 lg:px-8 lg:py-10">
        <section className="panel px-6 py-8 sm:px-8">
          <p className="text-xs uppercase tracking-[0.35em] text-slate-400">
            Camera lab
          </p>
          <div className="mt-4 flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
            <div className="max-w-2xl">
              <h1 className="text-4xl font-semibold tracking-tight text-white">
                Camera plus exercise dashboard prototype
              </h1>
              <p className="mt-3 text-sm leading-7 text-slate-300">
                Use this page to verify camera permissions, preview framing, and
                the full dashboard structure for future Raspberry Pi AI exercise
                stats, rep counting, and correction feedback.
              </p>
            </div>
            <div className="rounded-[28px] border border-white/10 bg-slate-950/70 px-5 py-4">
              <p className="text-xs uppercase tracking-[0.32em] text-slate-400">
                Integration note
              </p>
              <p className="mt-2 max-w-sm text-sm leading-7 text-slate-300">
                Detection on this page is intentionally mocked after the camera
                starts. Replace the placeholder state with real AI payloads later.
              </p>
            </div>
          </div>
        </section>

        <section className="space-y-6 xl:hidden">
          <div className="space-y-6">
            <CameraPreview
              onCameraActiveChange={setCameraActive}
              onDetectionChange={setDetection}
            />

            <section className="panel p-6 xl:hidden">
              <p className="text-xs uppercase tracking-[0.35em] text-slate-400">
                Trainer mode
              </p>
              <div className="mt-4 rounded-[28px] border border-cyan-400/20 bg-cyan-400/10 p-5">
                <p className="text-4xl font-semibold text-white">
                  REP {activeData.completedReps} / {activeData.targetReps}
                </p>
                <p className="mt-3 text-lg font-medium text-cyan-50">
                  FORM: {activeData.formScore >= 75 ? "GOOD" : "NEEDS WORK"}
                </p>
                <p className="mt-4 text-base font-medium uppercase tracking-[0.18em] text-white">
                  {mobileFeedbackHeadline}
                </p>
              </div>
            </section>

            <section className="xl:hidden">
              <RepCounter
                completedReps={activeData.completedReps}
                targetReps={activeData.targetReps}
                correctReps={activeData.correctReps}
                incorrectReps={activeData.incorrectReps}
              />
            </section>

            <section className="xl:hidden">
              <FeedbackPanel
                suggestions={feedbackSuggestions}
                activeSuggestion={cameraActive ? activeData.activeSuggestion : null}
              />
            </section>

            <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
              {statusCards.map((card) => (
                <StatusCard
                  key={card.label}
                  label={card.label}
                  value={card.value}
                  tone={card.tone as "good" | "neutral" | "warn"}
                />
              ))}
            </div>

            <section className="xl:hidden">
              <CurrentExercisePanel data={activeData} />
            </section>
            <section className="xl:hidden">
              <WorkoutStatsPanel data={activeData} />
            </section>
            <section className="xl:hidden">
              <RaspberryPiStatus status={activeData.raspberryPiStatus} />
            </section>
            <section className="xl:hidden">
              <MistakeSummary mistakes={activeData.mistakes} />
            </section>
            <section className="xl:hidden">
              <RepBreakdown reps={activeData.repResults} compact />
            </section>
            <SessionTimeline events={activeData.sessionTimeline} />
          </div>
        </section>

        <section className="hidden xl:grid xl:grid-cols-3 xl:gap-6">
          <div className="space-y-6 xl:col-span-2">
            <CameraPreview
              onCameraActiveChange={setCameraActive}
              onDetectionChange={setDetection}
            />

            <div className="grid gap-4 xl:grid-cols-3">
              {statusCards.map((card) => (
                <StatusCard
                  key={card.label}
                  label={card.label}
                  value={card.value}
                  tone={card.tone as "good" | "neutral" | "warn"}
                />
              ))}
            </div>

            <SessionTimeline events={activeData.sessionTimeline} />
          </div>

          <div className="space-y-6">
            <FeedbackPanel
              suggestions={feedbackSuggestions}
              activeSuggestion={cameraActive ? activeData.activeSuggestion : null}
            />

            <section className="panel p-6">
              <p className="text-xs uppercase tracking-[0.35em] text-slate-400">
                Trainer mode
              </p>
              <div className="mt-4 rounded-[28px] border border-cyan-400/20 bg-cyan-400/10 p-5">
                <p className="text-4xl font-semibold text-white">
                  REP {activeData.completedReps} / {activeData.targetReps}
                </p>
                <p className="mt-3 text-lg font-medium text-cyan-50">
                  FORM: {activeData.formScore >= 75 ? "GOOD" : "NEEDS WORK"}
                </p>
                <p className="mt-4 text-base font-medium uppercase tracking-[0.18em] text-white">
                  {mobileFeedbackHeadline}
                </p>
              </div>
            </section>

            <RepCounter
              completedReps={activeData.completedReps}
              targetReps={activeData.targetReps}
              correctReps={activeData.correctReps}
              incorrectReps={activeData.incorrectReps}
            />

            <CurrentExercisePanel data={activeData} />
            <FormScoreCard
              formScore={activeData.formScore}
              scores={activeData.scores}
            />
            <RaspberryPiStatus status={activeData.raspberryPiStatus} />
          </div>

          <div className="xl:col-span-2">
            <WorkoutStatsPanel data={activeData} />
          </div>

          <div>
            <MistakeSummary mistakes={activeData.mistakes} />
          </div>

          <div className="xl:col-span-3">
            <RepBreakdown reps={activeData.repResults} />
          </div>
        </section>

        <section>
          <DebugPayloadPanel payload={futurePayloadExample} />
        </section>
      </div>
    </main>
  );
}
