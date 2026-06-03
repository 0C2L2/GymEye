import type {
  ExerciseDetectionResult,
  ExerciseMistake,
  SessionTimelineEvent
} from "@/types/detection";
import type { RaspberryPiConnectionStatus } from "@/types/raspberryPi";
import { getMockRepResults } from "@/lib/mockSessions";

// This is temporary mock data.
// Later this should be replaced with live data from Raspberry Pi AI through WebSocket or API.
export function getMockDetectionResult(): ExerciseDetectionResult {
  return {
    cameraActive: true,
    personDetected: true,
    faceDetected: true,
    bodyVisible: "full",
    exercise: "Squat demo",
    set: 2,
    targetReps: 15,
    completedReps: 12,
    correctReps: 9,
    incorrectReps: 3,
    formScore: 82,
    confidence: 0.91,
    durationSeconds: 154,
    averageRepTimeSeconds: 3.8,
    caloriesEstimate: 18,
    scores: {
      balance: 88,
      rangeOfMotion: 76,
      speedControl: 84,
      posture: 79
    },
    mistakes: getMockLiveMistakes(),
    activeSuggestion: "Push your knees outward.",
    source: "Browser demo mode",
    currentPace: "Good",
    bestRepScore: 94,
    worstRepScore: 61,
    exerciseCategory: "Legs",
    musclesInvolved: ["Quads", "Glutes", "Hamstrings"],
    difficulty: "Beginner",
    activeFeedback: [
      "Keep your chest up.",
      "Push your knees outward.",
      "Slow down the movement.",
      "Keep your back neutral.",
      "Stand fully inside the camera frame."
    ],
    sessionTimeline: getMockSessionTimeline(),
    repResults: getMockRepResults(),
    raspberryPiStatus: getMockRaspberryPiStatus(),
    timestamp: "2026-06-03T00:00:00Z"
  };
}

export function getIdleSuggestions() {
  return [
    "Stand fully inside the camera frame.",
    "Keep your body visible from head to knees.",
    "Make sure lighting is clear.",
    "Exercise correction will appear here once Raspberry Pi AI is connected."
  ];
}

export function getMockSessionTimeline(): SessionTimelineEvent[] {
  return [
    { time: "00:04", event: "Person detected" },
    { time: "00:08", event: "Squat detected" },
    { time: "00:15", event: "Rep 1 completed" },
    { time: "00:19", event: "Rep 2 completed" },
    { time: "00:24", event: "Mistake detected: knees caving inward" },
    { time: "00:31", event: "Rep 3 completed" }
  ];
}

export function getMockLiveMistakes(): ExerciseMistake[] {
  return [
    {
      type: "knees_caving_inward",
      label: "Knees caving inward",
      severity: "medium",
      count: 2,
      suggestion: "Keep your knees aligned with your toes."
    },
    {
      type: "back_not_straight",
      label: "Back not straight",
      severity: "high",
      count: 1,
      suggestion: "Keep your chest up and spine neutral."
    },
    {
      type: "not_reaching_full_depth",
      label: "Not reaching full depth",
      severity: "low",
      count: 1,
      suggestion: "Lower until your hips reach at least knee level."
    }
  ];
}

// Later, replace this mock connection state with live WebSocket/API data from Raspberry Pi.
export function getMockRaspberryPiStatus(): RaspberryPiConnectionStatus {
  return {
    connected: false,
    mode: "demo",
    latencyMs: null,
    fps: null,
    modelName: "Demo placeholder",
    lastSignalAt: null,
    message: "Raspberry Pi AI is not connected. Showing browser demo data."
  };
}

export function getMockConnectedRaspberryPiStatus(): RaspberryPiConnectionStatus {
  return {
    connected: true,
    mode: "raspberry_pi",
    latencyMs: 42,
    fps: 24,
    modelName: "Gym Eye Pose Model v1",
    lastSignalAt: "Just now",
    message: "Receiving live exercise analysis from Raspberry Pi."
  };
}

export const futurePayloadExample: ExerciseDetectionResult = getMockDetectionResult();
