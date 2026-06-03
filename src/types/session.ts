export type RepStatus = "excellent" | "good" | "needs_work" | "poor";

export type RepResult = {
  repNumber: number;
  score: number;
  status: RepStatus;
  mistake: string | null;
  durationSeconds: number;
  correct: boolean;
};

export type WorkoutSessionSummary = {
  id: string;
  exercise: string;
  date: string;
  totalReps: number;
  correctReps: number;
  incorrectReps: number;
  averageFormScore: number;
  bestRepScore: number;
  worstRepScore: number;
  mostCommonMistake: string | null;
  durationSeconds: number;
  caloriesEstimate: number;
  repResults: RepResult[];
};

export type RecentWorkoutSession = {
  id: string;
  exercise: string;
  dateLabel: string;
  totalReps: number;
  formScore: number;
  mistakesCount: number;
  durationSeconds: number;
};
