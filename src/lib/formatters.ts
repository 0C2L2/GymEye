export function formatDuration(seconds: number) {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;

  return `${String(minutes).padStart(2, "0")}:${String(remainingSeconds).padStart(2, "0")}`;
}

export function formatPercent(value: number) {
  return `${Math.round(value)}%`;
}

export function formatConfidence(value: number) {
  return `${Math.round(value * 100)}%`;
}

export function formatRepTime(value: number) {
  return `${value.toFixed(1)}s`;
}

export function formatCalories(value: number) {
  return `${value} kcal`;
}

export function formatNullableNumber(value: number | null, suffix = "") {
  return value === null ? "—" : `${value}${suffix}`;
}
