import type { RaspberryPiConnectionStatus } from "@/types/raspberryPi";
import type { RepResult } from "@/types/session";

export type ExerciseMistake = {
  type: string;
  label: string;
  severity: "low" | "medium" | "high";
  count: number;
  suggestion: string;
};

export type SessionTimelineEvent = {
  time: string;
  event: string;
};

export type ExerciseDetectionResult = {
  cameraActive: boolean;
  personDetected: boolean;
  faceDetected: boolean;
  bodyVisible: "full" | "partial" | "none";
  exercise: string | null;
  set: number;
  targetReps: number;
  completedReps: number;
  correctReps: number;
  incorrectReps: number;
  formScore: number;
  confidence: number;
  durationSeconds: number;
  averageRepTimeSeconds: number;
  caloriesEstimate: number;
  scores: {
    balance: number;
    rangeOfMotion: number;
    speedControl: number;
    posture: number;
  };
  mistakes: ExerciseMistake[];
  activeSuggestion: string | null;
  source: "Browser demo mode";
  currentPace: "Good" | "Steady" | "Needs work";
  bestRepScore: number;
  worstRepScore: number;
  exerciseCategory: string;
  musclesInvolved: string[];
  difficulty: string;
  activeFeedback: string[];
  sessionTimeline: SessionTimelineEvent[];
  repResults: RepResult[];
  raspberryPiStatus: RaspberryPiConnectionStatus;
  timestamp: string;
};
