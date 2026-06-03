from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field

AnalysisSource = Literal["demo", "browser_ai", "backend", "raspberry_pi", "gazebo"]
BodyVisibility = Literal["full", "partial", "none"]
MistakeSeverity = Literal["low", "medium", "high"]
RepStatus = Literal["excellent", "good", "needs_work", "poor"]


class ExerciseMistake(BaseModel):
    type: str = "unknown"
    label: str = "Unknown issue"
    severity: MistakeSeverity = "low"
    count: int = 1
    suggestion: str = ""


class RepResult(BaseModel):
    repNumber: int = 0
    score: int = 0
    status: RepStatus = "needs_work"
    mistake: Optional[str] = None
    durationSeconds: Optional[float] = None
    correct: bool = False


class ScoreBreakdown(BaseModel):
    balance: Optional[float] = None
    rangeOfMotion: Optional[float] = None
    speedControl: Optional[float] = None
    posture: Optional[float] = None


class AngleBreakdown(BaseModel):
    leftKnee: Optional[float] = None
    rightKnee: Optional[float] = None
    leftHip: Optional[float] = None
    rightHip: Optional[float] = None
    leftElbow: Optional[float] = None
    rightElbow: Optional[float] = None
    shoulder: Optional[float] = None
    torso: Optional[float] = None


class RobotPose(BaseModel):
    x: Optional[float] = None
    y: Optional[float] = None
    yaw: Optional[float] = None


class GymEyeAnalysis(BaseModel):
    cameraActive: bool = False
    personDetected: bool = False
    faceDetected: bool = False
    bodyVisible: BodyVisibility = "none"
    exercise: Optional[str] = None
    set: int = 1
    targetReps: int = 15
    completedReps: int = 0
    correctReps: int = 0
    incorrectReps: int = 0
    formScore: Optional[float] = None
    confidence: Optional[float] = None
    durationSeconds: int = 0
    averageRepTimeSeconds: Optional[float] = None
    caloriesEstimate: Optional[float] = None
    scores: ScoreBreakdown = Field(default_factory=ScoreBreakdown)
    angles: AngleBreakdown = Field(default_factory=AngleBreakdown)
    mistakes: List[ExerciseMistake] = Field(default_factory=list)
    activeSuggestion: Optional[str] = None
    repResults: List[RepResult] = Field(default_factory=list)
    source: AnalysisSource = "demo"
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    robotPose: Optional[RobotPose] = None
    poseLandmarks: Optional[List[List[float]]] = None
    rawPayload: Dict[str, Any] = Field(default_factory=dict)


def _to_iso_timestamp(raw: Any) -> str:
    if isinstance(raw, str) and raw:
        return raw
    if isinstance(raw, (int, float)):
        return datetime.fromtimestamp(raw, tz=timezone.utc).isoformat()
    return datetime.now(timezone.utc).isoformat()


def _to_int(value: Any, default: int) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def _to_float(value: Any, default: Optional[float]) -> Optional[float]:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _to_bool(value: Any, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "1", "yes", "on"}:
            return True
        if lowered in {"false", "0", "no", "off"}:
            return False
    if isinstance(value, (int, float)):
        return bool(value)
    return default


def _normalize_visibility(value: Any, default: BodyVisibility) -> BodyVisibility:
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"full", "partial", "none"}:
            return lowered  # type: ignore[return-value]
    return default


def _normalize_source(value: Any, default: AnalysisSource) -> AnalysisSource:
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"demo", "browser_ai", "backend", "raspberry_pi", "gazebo"}:
            return lowered  # type: ignore[return-value]
        if lowered in {"webcam", "ros2_camera", "browser"}:
            return "browser_ai"
        if lowered in {"sim", "simulation"}:
            return "gazebo"
        if lowered in {"pi", "rpi"}:
            return "raspberry_pi"
    return default


def _score_to_status(score: int) -> RepStatus:
    if score >= 90:
        return "excellent"
    if score >= 75:
        return "good"
    if score >= 50:
        return "needs_work"
    return "poor"


def _normalize_mistake(item: Any) -> ExerciseMistake:
    if isinstance(item, str):
        return ExerciseMistake(type=item.lower().replace(" ", "_"), label=item, suggestion="")
    if not isinstance(item, dict):
        return ExerciseMistake()
    label = str(item.get("label") or item.get("type") or "Unknown issue")
    return ExerciseMistake(
        type=str(item.get("type") or label.lower().replace(" ", "_")),
        label=label,
        severity=item.get("severity") if item.get("severity") in {"low", "medium", "high"} else "low",
        count=_to_int(item.get("count"), 1),
        suggestion=str(item.get("suggestion") or item.get("feedback") or ""),
    )


def _normalize_rep_result(item: Any, index: int) -> RepResult:
    if not isinstance(item, dict):
        score = _to_int(item, 0)
        return RepResult(
            repNumber=index + 1,
            score=score,
            status=_score_to_status(score),
            correct=score >= 75,
        )
    score = _to_int(item.get("score"), 0)
    status = item.get("status")
    return RepResult(
        repNumber=_to_int(item.get("repNumber") or item.get("rep_number"), index + 1),
        score=score,
        status=status if status in {"excellent", "good", "needs_work", "poor"} else _score_to_status(score),
        mistake=item.get("mistake"),
        durationSeconds=_to_float(item.get("durationSeconds") or item.get("duration_seconds"), None),
        correct=_to_bool(item.get("correct"), score >= 75),
    )


def _update_if_present(raw: Dict[str, Any], keys: List[str], callback) -> None:
    for key in keys:
        if key in raw:
            callback(raw.get(key))
            return


def normalize_analysis_payload(
    raw: Dict[str, Any],
    previous: Optional[GymEyeAnalysis] = None,
    fallback_source: AnalysisSource = "backend",
) -> GymEyeAnalysis:
    previous = previous.model_copy(deep=True) if previous else GymEyeAnalysis()
    normalized = previous
    normalized.rawPayload = raw

    _update_if_present(raw, ["cameraActive", "camera_active"], lambda value: setattr(normalized, "cameraActive", _to_bool(value, normalized.cameraActive)))
    _update_if_present(raw, ["personDetected", "person_detected"], lambda value: setattr(normalized, "personDetected", _to_bool(value, normalized.personDetected)))
    _update_if_present(raw, ["faceDetected", "face_detected"], lambda value: setattr(normalized, "faceDetected", _to_bool(value, normalized.faceDetected)))
    _update_if_present(raw, ["bodyVisible", "body_visible"], lambda value: setattr(normalized, "bodyVisible", _normalize_visibility(value, normalized.bodyVisible)))
    _update_if_present(raw, ["exercise", "exercise_name"], lambda value: setattr(normalized, "exercise", str(value) if value not in {None, ""} else None))
    _update_if_present(raw, ["set", "current_set"], lambda value: setattr(normalized, "set", max(1, _to_int(value, normalized.set))))
    _update_if_present(raw, ["targetReps", "target_reps"], lambda value: setattr(normalized, "targetReps", max(0, _to_int(value, normalized.targetReps))))
    _update_if_present(raw, ["completedReps", "rep_count", "reps"], lambda value: setattr(normalized, "completedReps", max(0, _to_int(value, normalized.completedReps))))
    _update_if_present(raw, ["correctReps", "correct_reps"], lambda value: setattr(normalized, "correctReps", max(0, _to_int(value, normalized.correctReps))))
    _update_if_present(raw, ["incorrectReps", "incorrect_reps"], lambda value: setattr(normalized, "incorrectReps", max(0, _to_int(value, normalized.incorrectReps))))
    _update_if_present(raw, ["formScore", "form_score", "score"], lambda value: setattr(normalized, "formScore", _to_float(value, normalized.formScore)))
    _update_if_present(raw, ["confidence"], lambda value: setattr(normalized, "confidence", _to_float(value, normalized.confidence)))
    _update_if_present(raw, ["durationSeconds", "duration_seconds"], lambda value: setattr(normalized, "durationSeconds", max(0, _to_int(value, normalized.durationSeconds))))
    _update_if_present(raw, ["averageRepTimeSeconds", "average_rep_time_seconds"], lambda value: setattr(normalized, "averageRepTimeSeconds", _to_float(value, normalized.averageRepTimeSeconds)))
    _update_if_present(raw, ["caloriesEstimate", "calories_estimate"], lambda value: setattr(normalized, "caloriesEstimate", _to_float(value, normalized.caloriesEstimate)))
    _update_if_present(raw, ["activeSuggestion", "feedback", "suggestion"], lambda value: setattr(normalized, "activeSuggestion", str(value) if value not in {None, ""} else None))
    _update_if_present(raw, ["source"], lambda value: setattr(normalized, "source", _normalize_source(value, fallback_source)))
    if "timestamp" in raw:
        normalized.timestamp = _to_iso_timestamp(raw.get("timestamp"))
    elif raw:
        normalized.timestamp = _to_iso_timestamp(None)
    _update_if_present(raw, ["poseLandmarks", "pose_landmarks"], lambda value: setattr(normalized, "poseLandmarks", value if isinstance(value, list) else normalized.poseLandmarks))

    if "scores" in raw and isinstance(raw["scores"], dict):
        normalized.scores = ScoreBreakdown(
            balance=_to_float(raw["scores"].get("balance"), normalized.scores.balance),
            rangeOfMotion=_to_float(raw["scores"].get("rangeOfMotion") or raw["scores"].get("range_of_motion"), normalized.scores.rangeOfMotion),
            speedControl=_to_float(raw["scores"].get("speedControl") or raw["scores"].get("speed_control"), normalized.scores.speedControl),
            posture=_to_float(raw["scores"].get("posture"), normalized.scores.posture),
        )

    if "angles" in raw and isinstance(raw["angles"], dict):
        angles = raw["angles"]
        normalized.angles = AngleBreakdown(
            leftKnee=_to_float(angles.get("leftKnee") or angles.get("left_knee"), normalized.angles.leftKnee),
            rightKnee=_to_float(angles.get("rightKnee") or angles.get("right_knee") or angles.get("knee"), normalized.angles.rightKnee),
            leftHip=_to_float(angles.get("leftHip") or angles.get("left_hip"), normalized.angles.leftHip),
            rightHip=_to_float(angles.get("rightHip") or angles.get("right_hip") or angles.get("hip"), normalized.angles.rightHip),
            leftElbow=_to_float(angles.get("leftElbow") or angles.get("left_elbow"), normalized.angles.leftElbow),
            rightElbow=_to_float(angles.get("rightElbow") or angles.get("right_elbow") or angles.get("elbow"), normalized.angles.rightElbow),
            shoulder=_to_float(angles.get("shoulder"), normalized.angles.shoulder),
            torso=_to_float(angles.get("torso"), normalized.angles.torso),
        )

    if "mistakes" in raw and isinstance(raw["mistakes"], list):
        normalized.mistakes = [_normalize_mistake(item) for item in raw["mistakes"]]

    if "repResults" in raw and isinstance(raw["repResults"], list):
        normalized.repResults = [
            _normalize_rep_result(item, index) for index, item in enumerate(raw["repResults"])
        ]

    if "robot_pose" in raw or "robotPose" in raw:
        pose = raw.get("robotPose") or raw.get("robot_pose")
        if isinstance(pose, dict):
            normalized.robotPose = RobotPose(
                x=_to_float(pose.get("x"), normalized.robotPose.x if normalized.robotPose else None),
                y=_to_float(pose.get("y"), normalized.robotPose.y if normalized.robotPose else None),
                yaw=_to_float(pose.get("yaw"), normalized.robotPose.yaw if normalized.robotPose else None),
            )

    if normalized.correctReps == 0 and normalized.incorrectReps == 0 and normalized.completedReps > 0:
        inferred_correct = sum(1 for rep in normalized.repResults if rep.correct)
        inferred_incorrect = sum(1 for rep in normalized.repResults if not rep.correct)
        if normalized.repResults:
            normalized.correctReps = inferred_correct
            normalized.incorrectReps = inferred_incorrect

    if normalized.correctReps + normalized.incorrectReps > normalized.completedReps:
        normalized.completedReps = normalized.correctReps + normalized.incorrectReps

    if normalized.exercise and normalized.exercise.upper() != "UNKNOWN":
        normalized.cameraActive = _to_bool(
            raw.get("cameraActive"),
            normalized.cameraActive or normalized.source != "demo",
        )
        normalized.personDetected = _to_bool(
            raw.get("personDetected"),
            normalized.personDetected or True,
        )

    if normalized.personDetected and normalized.bodyVisible == "none":
        normalized.bodyVisible = "partial"

    if normalized.activeSuggestion is None and normalized.mistakes:
        normalized.activeSuggestion = normalized.mistakes[0].suggestion or normalized.mistakes[0].label

    if normalized.source == "demo" and fallback_source != "demo" and raw:
        normalized.source = fallback_source

    return normalized
