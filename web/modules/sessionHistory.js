const STORAGE_KEY = "gym-eye-session-history";

export function loadSessionHistory() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch (error) {
    return [];
  }
}

export function saveSessionHistory(history) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
}

export function buildSessionSummary(analysis) {
  const mistakes = analysis.mistakes || [];
  const mostCommon = mistakes
    .slice()
    .sort((a, b) => (b.count || 0) - (a.count || 0))[0];

  return {
    id: `${analysis.exercise || "session"}-${Date.now()}`,
    date: new Date().toISOString(),
    exercise: analysis.exercise || "Unknown",
    totalReps: analysis.completedReps || 0,
    correctReps: analysis.correctReps || 0,
    incorrectReps: analysis.incorrectReps || 0,
    averageFormScore: analysis.formScore ?? null,
    bestRepScore: Math.max(0, ...(analysis.repResults || []).map((rep) => rep.score || 0)),
    worstRepScore: Math.min(100, ...(analysis.repResults || []).map((rep) => rep.score || 100)),
    mostCommonMistake: mostCommon?.label || null,
    durationSeconds: analysis.durationSeconds || 0,
    caloriesEstimate: analysis.caloriesEstimate ?? null,
    repResults: analysis.repResults || [],
    source: analysis.source,
    activeSuggestion: analysis.activeSuggestion || null,
  };
}
