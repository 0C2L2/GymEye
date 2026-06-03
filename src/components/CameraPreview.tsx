"use client";

import { useEffect, useRef, useState } from "react";

import { requestCameraStream, stopCameraStream } from "@/lib/camera";
import { getMockDetectionResult } from "@/lib/mockDetection";
import type { ExerciseDetectionResult } from "@/types/detection";

type CameraPreviewProps = {
  onDetectionChange: (result: ExerciseDetectionResult | null) => void;
  onCameraActiveChange: (active: boolean) => void;
};

export function CameraPreview({
  onDetectionChange,
  onCameraActiveChange
}: CameraPreviewProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const detectionTimerRef = useRef<number | null>(null);

  const [isStarting, setIsStarting] = useState(false);
  const [isActive, setIsActive] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const clearDetectionTimer = () => {
    if (detectionTimerRef.current !== null) {
      window.clearTimeout(detectionTimerRef.current);
      detectionTimerRef.current = null;
    }
  };

  const handleStop = () => {
    clearDetectionTimer();
    stopCameraStream(streamRef.current);
    streamRef.current = null;

    if (videoRef.current) {
      videoRef.current.pause();
      videoRef.current.srcObject = null;
    }

    setIsActive(false);
    setIsStarting(false);
    setErrorMessage(null);
    onCameraActiveChange(false);
    onDetectionChange(null);
  };

  const handleStart = async () => {
    setIsStarting(true);
    setErrorMessage(null);

    try {
      const stream = await requestCameraStream();
      streamRef.current = stream;

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }

      setIsActive(true);
      onCameraActiveChange(true);
      onDetectionChange(null);

      // Placeholder browser-side demo detection.
      // Replace this timer-based mock with Raspberry Pi AI results over WebSocket/API later.
      clearDetectionTimer();
      detectionTimerRef.current = window.setTimeout(() => {
        onDetectionChange(getMockDetectionResult());
      }, 1600);
    } catch (error) {
      const message =
        error instanceof Error
          ? error.message
          : "Camera could not be started. Check browser permissions.";

      setErrorMessage(message);
      onCameraActiveChange(false);
      onDetectionChange(null);
    } finally {
      setIsStarting(false);
    }
  };

  useEffect(() => {
    return () => {
      handleStop();
    };
    // This cleanup should run once on unmount to avoid leaking media tracks.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <section className="panel overflow-hidden p-4 sm:p-5">
      <div
        className={`relative overflow-hidden rounded-[28px] border ${
          isActive
            ? "border-cyan-400/40 shadow-glow"
            : "border-white/10"
        } bg-slate-950`}
      >
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,rgba(34,211,238,0.14),transparent_40%)]" />
        <video
          ref={videoRef}
          className="aspect-[4/5] w-full bg-slate-950 object-cover sm:aspect-video"
          autoPlay
          muted
          playsInline
        />
        {!isActive ? (
          <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 px-6 text-center">
            <span className="rounded-full border border-cyan-400/20 bg-cyan-400/10 px-4 py-2 text-xs uppercase tracking-[0.3em] text-cyan-100">
              Camera preview
            </span>
            <h2 className="text-2xl font-semibold text-white">
              Ready when you are
            </h2>
            <p className="max-w-md text-sm leading-7 text-slate-300">
              Start the camera to test browser preview, placeholder presence
              detection, and the future AI feedback layout.
            </p>
          </div>
        ) : null}
      </div>

      <div className="mt-5 flex flex-col gap-3 sm:flex-row">
        <button
          type="button"
          onClick={handleStart}
          disabled={isStarting || isActive}
          className="inline-flex items-center justify-center rounded-full bg-gradient-to-r from-cyan-400 to-emerald-400 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:scale-[1.01] disabled:cursor-not-allowed disabled:opacity-60"
        >
          {isStarting ? "Starting camera..." : "Start Camera"}
        </button>
        <button
          type="button"
          onClick={handleStop}
          disabled={!isActive && !isStarting}
          className="inline-flex items-center justify-center rounded-full border border-white/15 bg-white/5 px-5 py-3 text-sm font-semibold text-white transition hover:bg-white/10 disabled:cursor-not-allowed disabled:opacity-50"
        >
          Stop Camera
        </button>
      </div>

      {errorMessage ? (
        <div className="mt-4 rounded-3xl border border-rose-400/20 bg-rose-400/10 px-4 py-3 text-sm text-rose-100">
          {errorMessage}
        </div>
      ) : null}

      <p className="mt-4 text-xs leading-6 text-slate-400">
        Camera runs entirely in the browser using <code>getUserMedia</code>. No
        Raspberry Pi AI logic is connected yet.
      </p>
    </section>
  );
}
