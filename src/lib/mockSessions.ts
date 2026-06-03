import type { ExerciseMistake } from "@/types/detection";
import type {
  RecentWorkoutSession,
  RepResult,
  WorkoutSessionSummary
} from "@/types/session";

export function getMockRepResults(): RepResult[] {
  return [
    {
      repNumber: 1,
      score: 91,
      status: "excellent",
      mistake: null,
      durationSeconds: 3.2,
      correct: true
    },
    {
      repNumber: 2,
      score: 88,
      status: "good",
      mistake: null,
      durationSeconds: 3.5,
      correct: true
    },
    {
      repNumber: 3,
      score: 64,
      status: "needs_work",
      mistake: "Knees caving inward",
      durationSeconds: 2.8,
      correct: false
    },
    {
      repNumber: 4,
      score: 72,
      status: "needs_work",
      mistake: "Not reaching full depth",
      durationSeconds: 3,
      correct: false
    },
    {
      repNumber: 5,
      score: 84,
      status: "good",
      mistake: null,
      durationSeconds: 3.4,
      correct: true
    },
    {
      repNumber: 6,
      score: 79,
      status: "good",
      mistake: null,
      durationSeconds: 3.5,
      correct: true
    },
    {
      repNumber: 7,
      score: 58,
      status: "poor",
      mistake: "Back angle dropped",
      durationSeconds: 2.9,
      correct: false
    },
    {
      repNumber: 8,
      score: 86,
      status: "good",
      mistake: null,
      durationSeconds: 3.6,
      correct: true
    },
    {
      repNumber: 9,
      score: 90,
      status: "excellent",
      mistake: null,
      durationSeconds: 3.7,
      correct: true
    },
    {
      repNumber: 10,
      score: 83,
      status: "good",
      mistake: null,
      durationSeconds: 3.4,
      correct: true
    },
    {
      repNumber: 11,
      score: 81,
      status: "good",
      mistake: null,
      durationSeconds: 3.2,
      correct: true
    },
    {
      repNumber: 12,
      score: 74,
      status: "needs_work",
      mistake: "Knees caving inward",
      durationSeconds: 3.1,
      correct: false
    },
    {
      repNumber: 13,
      score: 92,
      status: "excellent",
      mistake: null,
      durationSeconds: 3.6,
      correct: true
    },
    {
      repNumber: 14,
      score: 96,
      status: "excellent",
      mistake: null,
      durationSeconds: 3.5,
      correct: true
    },
    {
      repNumber: 15,
      score: 87,
      status: "good",
      mistake: null,
      durationSeconds: 3.4,
      correct: true
    }
  ];
}

export function getMockSessionSummary(): WorkoutSessionSummary {
  return {
    id: "session-squat-2026-06-03",
    exercise: "Squat",
    date: "2026-06-03",
    totalReps: 15,
    correctReps: 12,
    incorrectReps: 3,
    averageFormScore: 84,
    bestRepScore: 96,
    worstRepScore: 58,
    mostCommonMistake: "Knees caving inward",
    durationSeconds: 222,
    caloriesEstimate: 27,
    repResults: getMockRepResults()
  };
}

export function getMockRecentSessions(): RecentWorkoutSession[] {
  return [
    {
      id: "session-1",
      exercise: "Squat",
      dateLabel: "Today",
      totalReps: 15,
      formScore: 84,
      mistakesCount: 3,
      durationSeconds: 222
    },
    {
      id: "session-2",
      exercise: "Push-up",
      dateLabel: "Yesterday",
      totalReps: 20,
      formScore: 79,
      mistakesCount: 4,
      durationSeconds: 245
    },
    {
      id: "session-3",
      exercise: "Deadlift",
      dateLabel: "2 days ago",
      totalReps: 10,
      formScore: 76,
      mistakesCount: 3,
      durationSeconds: 186
    },
    {
      id: "session-4",
      exercise: "Shoulder Press",
      dateLabel: "3 days ago",
      totalReps: 12,
      formScore: 82,
      mistakesCount: 2,
      durationSeconds: 198
    }
  ];
}

export function getMockCommonMistakes(): ExerciseMistake[] {
  return [
    {
      type: "back_not_straight",
      label: "Back not straight",
      severity: "high",
      count: 12,
      suggestion: "Keep your chest up and brace your core."
    },
    {
      type: "knees_caving_inward",
      label: "Knees caving inward",
      severity: "medium",
      count: 8,
      suggestion: "Track your knees over your toes."
    },
    {
      type: "moving_too_fast",
      label: "Moving too fast",
      severity: "medium",
      count: 7,
      suggestion: "Use a slower controlled descent."
    },
    {
      type: "not_full_range",
      label: "Not full range of motion",
      severity: "low",
      count: 5,
      suggestion: "Reach full depth before driving back up."
    }
  ];
}
