const VALID_SOURCES = new Set(["demo", "browser_ai", "backend", "raspberry_pi", "gazebo"]);
const VALID_VISIBILITY = new Set(["full", "partial", "none"]);
const VALID_REP_STATUS = new Set(["excellent", "good", "needs_work", "poor"]);
const VALID_SEVERITY = new Set(["low", "medium", "high"]);

function toInt(value, fallback = 0) {
  const next = Number.parseInt(value, 10);
  return Number.isFinite(next) ? next : fallback;
}

function toFloat(value, fallback = null) {
  if (value === null || value === undefined || value === "") {
    return fallback;
  }
  const next = Number(value);
  return Number.isFinite(next) ? next : fallback;
}

function toBool(value, fallback = false) {
  if (typeof value === "boolean") return value;
  if (typeof value === "string") {
    const lowered = value.toLowerCase();
    if (["true", "1", "yes", "on"].includes(lowered)) return true;
    if (["false", "0", "no", "off"].includes(lowered)) return false;
  }
  if (typeof value === "number") return Boolean(value);
  return fallback;
}

function normalizeSource(value, fallback = "demo") {
  if (typeof value !== "string") return fallback;
  const lowered = value.toLowerCase();
  if (VALID_SOURCES.has(lowered)) return lowered;
  if (["webcam", "browser", "ros2_camera"].includes(lowered)) return "browser_ai";
  if (["sim", "simulation"].includes(lowered)) return "gazebo";
  if (["pi", "rpi"].includes(lowered)) return "raspberry_pi";
  return fallback;
}

function normalizeVisibility(value, fallback = "none") {
  if (typeof value !== "string") return fallback;
  const lowered = value.toLowerCase();
  return VALID_VISIBILITY.has(lowered) ? lowered : fallback;
}

function scoreToStatus(score) {
  if (score >= 90) return "excellent";
  if (score >= 75) return "good";
  if (score >= 50) return "needs_work";
  return "poor";
}

function normalizeMistake(item) {
  if (typeof item === "string") {
    return {
      type: item.toLowerCase().replace(/\s+/g, "_"),
      label: item,
      severity: "low",
      count: 1,
      suggestion: "",
    };
  }

  if (!item || typeof item !== "object") {
    return {
      type: "unknown",
      label: "Unknown issue",
      severity: "low",
      count: 1,
      suggestion: "",
    };
  }

  const label = item.label || item.type || "Unknown issue";
  return {
    type: item.type || String(label).toLowerCase().replace(/\s+/g, "_"),
    label,
    severity: VALID_SEVERITY.has(item.severity) ? item.severity : "low",
    count: toInt(item.count, 1),
    suggestion: item.suggestion || item.feedback || "",
  };
}

function normalizeRepResult(item, index) {
  if (!item || typeof item !== "object") {
    const score = toInt(item, 0);
    return {
      repNumber: index + 1,
      score,
      status: scoreToStatus(score),
      mistake: null,
      durationSeconds: null,
      correct: score >= 75,
    };
  }

  const score = toInt(item.score, 0);
  return {
    repNumber: toInt(item.repNumber ?? item.rep_number, index + 1),
    score,
    status: VALID_REP_STATUS.has(item.status) ? item.status : scoreToStatus(score),
    mistake: item.mistake || null,
    durationSeconds: toFloat(item.durationSeconds ?? item.duration_seconds, null),
    correct: toBool(item.correct, score >= 75),
  };
}

function normalizeTimestamp(value) {
  if (typeof value === "string" && value) return value;
  if (typeof value === "number") return new Date(value * 1000).toISOString();
  return new Date().toISOString();
}

export function normalizeAnalysisPayload(raw, source = "demo", previous = null) {
  const base = previous ? structuredClone(previous) : {};
  const payload = raw && typeof raw === "object" ? raw : {};

  const normalized = {
    cameraActive: toBool(payload.cameraActive ?? payload.camera_active, base.cameraActive ?? false),
    personDetected: toBool(payload.personDetected ?? payload.person_detected, base.personDetected ?? false),
    faceDetected: toBool(payload.faceDetected ?? payload.face_detected, base.faceDetected ?? false),
    bodyVisible: normalizeVisibility(payload.bodyVisible ?? payload.body_visible, base.bodyVisible ?? "none"),
    exercise: payload.exercise ?? payload.exercise_name ?? base.exercise ?? null,
    set: Math.max(1, toInt(payload.set ?? payload.current_set, base.set ?? 1)),
    targetReps: Math.max(0, toInt(payload.targetReps ?? payload.target_reps, base.targetReps ?? 15)),
    completedReps: Math.max(0, toInt(payload.completedReps ?? payload.rep_count ?? payload.reps, base.completedReps ?? 0)),
    correctReps: Math.max(0, toInt(payload.correctReps ?? payload.correct_reps, base.correctReps ?? 0)),
    incorrectReps: Math.max(0, toInt(payload.incorrectReps ?? payload.incorrect_reps, base.incorrectReps ?? 0)),
    formScore: toFloat(payload.formScore ?? payload.form_score ?? payload.score, base.formScore ?? null),
    confidence: toFloat(payload.confidence, base.confidence ?? null),
    durationSeconds: Math.max(0, toInt(payload.durationSeconds ?? payload.duration_seconds, base.durationSeconds ?? 0)),
    averageRepTimeSeconds: toFloat(payload.averageRepTimeSeconds ?? payload.average_rep_time_seconds, base.averageRepTimeSeconds ?? null),
    caloriesEstimate: toFloat(payload.caloriesEstimate ?? payload.calories_estimate, base.caloriesEstimate ?? null),
    scores: {
      balance: toFloat(payload.scores?.balance, base.scores?.balance ?? null),
      rangeOfMotion: toFloat(payload.scores?.rangeOfMotion ?? payload.scores?.range_of_motion, base.scores?.rangeOfMotion ?? null),
      speedControl: toFloat(payload.scores?.speedControl ?? payload.scores?.speed_control, base.scores?.speedControl ?? null),
      posture: toFloat(payload.scores?.posture, base.scores?.posture ?? null),
    },
    angles: {
      leftKnee: toFloat(payload.angles?.leftKnee ?? payload.angles?.left_knee, base.angles?.leftKnee ?? null),
      rightKnee: toFloat(payload.angles?.rightKnee ?? payload.angles?.right_knee ?? payload.angles?.knee, base.angles?.rightKnee ?? null),
      leftHip: toFloat(payload.angles?.leftHip ?? payload.angles?.left_hip, base.angles?.leftHip ?? null),
      rightHip: toFloat(payload.angles?.rightHip ?? payload.angles?.right_hip ?? payload.angles?.hip, base.angles?.rightHip ?? null),
      leftElbow: toFloat(payload.angles?.leftElbow ?? payload.angles?.left_elbow, base.angles?.leftElbow ?? null),
      rightElbow: toFloat(payload.angles?.rightElbow ?? payload.angles?.right_elbow ?? payload.angles?.elbow, base.angles?.rightElbow ?? null),
      shoulder: toFloat(payload.angles?.shoulder, base.angles?.shoulder ?? null),
      torso: toFloat(payload.angles?.torso, base.angles?.torso ?? null),
    },
    mistakes: Array.isArray(payload.mistakes) ? payload.mistakes.map(normalizeMistake) : base.mistakes ?? [],
    activeSuggestion: payload.activeSuggestion ?? payload.feedback ?? payload.suggestion ?? base.activeSuggestion ?? null,
    repResults: Array.isArray(payload.repResults)
      ? payload.repResults.map(normalizeRepResult)
      : base.repResults ?? [],
    source: normalizeSource(payload.source, normalizeSource(base.source, source)),
    timestamp: normalizeTimestamp(payload.timestamp ?? base.timestamp),
    robotPose: payload.robotPose ?? payload.robot_pose ?? base.robotPose ?? null,
    poseLandmarks: payload.poseLandmarks ?? payload.pose_landmarks ?? base.poseLandmarks ?? null,
    rawPayload: payload,
  };

  if (normalized.correctReps === 0 && normalized.incorrectReps === 0 && normalized.repResults.length > 0) {
    normalized.correctReps = normalized.repResults.filter((rep) => rep.correct).length;
    normalized.incorrectReps = normalized.repResults.filter((rep) => !rep.correct).length;
  }

  if (normalized.correctReps + normalized.incorrectReps > normalized.completedReps) {
    normalized.completedReps = normalized.correctReps + normalized.incorrectReps;
  }

  if (normalized.personDetected && normalized.bodyVisible === "none") {
    normalized.bodyVisible = "partial";
  }

  if (normalized.exercise && String(normalized.exercise).toUpperCase() !== "UNKNOWN") {
    normalized.cameraActive = normalized.cameraActive || normalized.source !== "demo";
    normalized.personDetected = normalized.personDetected || true;
  }

  if (!normalized.activeSuggestion && normalized.mistakes.length > 0) {
    normalized.activeSuggestion = normalized.mistakes[0].suggestion || normalized.mistakes[0].label;
  }

  return normalized;
}
