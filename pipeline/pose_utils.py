"""Shared pose estimation utilities used by pipeline and ROS2 nodes.

Import this module from webcam_pose.py or any ROS2 node by adding the
pipeline/ directory to sys.path first:

    import sys, pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "pipeline"))
    from pose_utils import ...
"""
from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import numpy as np


# ---------------------------------------------------------------------------
# One-Euro adaptive low-pass filter
# ---------------------------------------------------------------------------

class OneEuroFilter:
    """Adaptive low-pass filter that reduces jitter without adding lag."""

    def __init__(
        self,
        freq: float = 30.0,
        min_cutoff: float = 0.5,
        beta: float = 0.007,
        d_cutoff: float = 1.0,
    ) -> None:
        self.freq = freq
        self.min_cutoff = min_cutoff
        self.beta = beta
        self.d_cutoff = d_cutoff
        self._x_prev: Optional[float] = None
        self._dx_prev: float = 0.0

    def _alpha(self, cutoff: float) -> float:
        te = 1.0 / self.freq
        tau = 1.0 / (2.0 * math.pi * cutoff)
        return 1.0 / (1.0 + tau / te)

    def filter(self, value: float) -> float:
        if self._x_prev is None:
            self._x_prev = value
            return value
        te = 1.0 / self.freq
        derivative = (value - self._x_prev) / te
        alpha_d = self._alpha(self.d_cutoff)
        dx_hat = alpha_d * derivative + (1.0 - alpha_d) * self._dx_prev
        cutoff = self.min_cutoff + self.beta * abs(dx_hat)
        alpha = self._alpha(cutoff)
        filtered = alpha * value + (1.0 - alpha) * self._x_prev
        self._x_prev = filtered
        self._dx_prev = dx_hat
        return filtered


class LandmarkSmoother:
    """Per-landmark OneEuroFilter applied independently on x, y, z axes."""

    def __init__(self, freq: float = 30.0) -> None:
        self._filters: Dict[int, Dict[str, OneEuroFilter]] = {}
        self.freq = freq

    def _get(self, idx: int) -> Dict[str, OneEuroFilter]:
        if idx not in self._filters:
            self._filters[idx] = {
                ax: OneEuroFilter(self.freq) for ax in ("x", "y", "z")
            }
        return self._filters[idx]

    def smooth(self, landmarks: Any) -> list:
        """Smooth a MediaPipe landmark list. Returns a list of _Point objects."""
        result = []
        for i, lm in enumerate(landmarks):
            f = self._get(i)
            x = f["x"].filter(lm.x)
            y = f["y"].filter(lm.y)
            z = f["z"].filter(getattr(lm, "z", 0.0))
            result.append(_Point(x, y, z, getattr(lm, "visibility", 1.0)))
        return result


class _Point:
    __slots__ = ("x", "y", "z", "visibility")

    def __init__(self, x: float, y: float, z: float, visibility: float) -> None:
        self.x = x
        self.y = y
        self.z = z
        self.visibility = visibility


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------

def calculate_angle(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> float:
    """Return the angle (degrees) at joint b formed by the a-b-c triplet."""
    ab = a - b
    cb = c - b
    radians = math.atan2(cb[1], cb[0]) - math.atan2(ab[1], ab[0])
    angle = abs(radians * 180.0 / math.pi)
    return 360.0 - angle if angle > 180.0 else angle


def extract_landmarks(lm_list: Any) -> Dict[str, np.ndarray]:
    """Extract named 2-D landmark arrays from a MediaPipe landmark sequence."""
    lm = lm_list
    return {
        "left_shoulder":  np.array([lm[11].x, lm[11].y]),
        "right_shoulder": np.array([lm[12].x, lm[12].y]),
        "shoulder":       np.array([lm[12].x, lm[12].y]),
        "left_hip":       np.array([lm[23].x, lm[23].y]),
        "right_hip":      np.array([lm[24].x, lm[24].y]),
        "hip":            np.array([lm[24].x, lm[24].y]),
        "left_knee":      np.array([lm[25].x, lm[25].y]),
        "right_knee":     np.array([lm[26].x, lm[26].y]),
        "knee":           np.array([lm[26].x, lm[26].y]),
        "left_ankle":     np.array([lm[27].x, lm[27].y]),
        "right_ankle":    np.array([lm[28].x, lm[28].y]),
        "ankle":          np.array([lm[28].x, lm[28].y]),
        "left_elbow":     np.array([lm[13].x, lm[13].y]),
        "right_elbow":    np.array([lm[14].x, lm[14].y]),
        "elbow":          np.array([lm[14].x, lm[14].y]),
        "left_wrist":     np.array([lm[15].x, lm[15].y]),
        "right_wrist":    np.array([lm[16].x, lm[16].y]),
        "wrist":          np.array([lm[16].x, lm[16].y]),
    }


# ---------------------------------------------------------------------------
# Exercise classification
# ---------------------------------------------------------------------------

def classify_exercise(landmarks: Dict[str, np.ndarray]) -> str:
    """Classify the current exercise from named body landmark positions."""
    shoulder = landmarks["shoulder"]
    hip      = landmarks["hip"]
    ankle    = landmarks["ankle"]
    elbow    = landmarks["elbow"]
    wrist    = landmarks["wrist"]

    is_horizontal = (
        abs(shoulder[1] - hip[1]) < 0.15
        and abs(hip[1] - ankle[1]) < 0.15
    )
    is_vertical = (
        abs(shoulder[0] - hip[0]) < 0.15
        and abs(hip[0] - ankle[0]) < 0.15
    )

    if is_horizontal:
        elbow_angle = calculate_angle(shoulder, elbow, wrist)
        return "PUSH_UP" if elbow_angle < 120 else "PLANK"
    if is_vertical:
        return "SQUAT"
    return "UNKNOWN"


# ---------------------------------------------------------------------------
# Rep counting state + logic
# ---------------------------------------------------------------------------

@dataclass
class RepState:
    exercise: str = "UNKNOWN"
    stage: str = "UP"
    reps: int = 0
    correct_reps: int = 0
    incorrect_reps: int = 0
    rep_results: List[Dict] = field(default_factory=list)
    last_rep_time: float = field(default_factory=time.time)


def update_reps(
    exercise: str,
    landmarks: Dict[str, np.ndarray],
    state: RepState,
) -> str:
    """Update rep count / stage; return a real-time feedback string."""
    feedback = ""

    if exercise == "SQUAT":
        knee_angle = calculate_angle(
            landmarks["hip"], landmarks["knee"], landmarks["ankle"]
        )
        if knee_angle > 165:
            state.stage = "UP"
        elif knee_angle < 95 and state.stage == "UP":
            state.stage = "DOWN"
            now = time.time()
            duration = round(now - state.last_rep_time, 2)
            state.last_rep_time = now
            state.reps += 1
            correct = knee_angle < 90
            score = 92 if correct else 68
            feedback = "Good depth" if correct else "Go deeper"
            if correct:
                state.correct_reps += 1
            else:
                state.incorrect_reps += 1
            state.rep_results.append({
                "repNumber": state.reps,
                "score": score,
                "status": "excellent" if score >= 90 else "good" if score >= 75 else "needs_work",
                "correct": correct,
                "durationSeconds": duration,
                "mistake": None if correct else "insufficient_depth",
            })
        elif 95 <= knee_angle < 130 and state.stage == "UP":
            feedback = "Go lower"

    elif exercise == "PUSH_UP":
        elbow_angle = calculate_angle(
            landmarks["shoulder"], landmarks["elbow"], landmarks["wrist"]
        )
        if elbow_angle > 160:
            state.stage = "UP"
        elif elbow_angle < 90 and state.stage == "UP":
            state.stage = "DOWN"
            now = time.time()
            duration = round(now - state.last_rep_time, 2)
            state.last_rep_time = now
            state.reps += 1
            shoulder = landmarks["shoulder"]
            hip      = landmarks["hip"]
            ankle    = landmarks["ankle"]
            body_straight = (
                abs(shoulder[1] - hip[1]) < 0.10
                and abs(hip[1] - ankle[1]) < 0.10
            )
            correct = body_straight
            score = 88 if correct else 62
            feedback = "Good form" if correct else "Keep body straight"
            if correct:
                state.correct_reps += 1
            else:
                state.incorrect_reps += 1
            state.rep_results.append({
                "repNumber": state.reps,
                "score": score,
                "status": "good" if score >= 75 else "needs_work",
                "correct": correct,
                "durationSeconds": duration,
                "mistake": None if correct else "body_not_straight",
            })
        elif 90 <= elbow_angle < 130 and state.stage == "UP":
            feedback = "Lower your chest"

    elif exercise == "PLANK":
        shoulder = landmarks["shoulder"]
        hip      = landmarks["hip"]
        ankle    = landmarks["ankle"]
        sh_diff  = abs(shoulder[1] - hip[1])
        ha_diff  = abs(hip[1] - ankle[1])
        if sh_diff > 0.12:
            feedback = "Raise your hips" if hip[1] > shoulder[1] else "Lower your hips"
        elif ha_diff > 0.12:
            feedback = "Straighten your legs"
        else:
            feedback = "Hold steady"

    return feedback


# ---------------------------------------------------------------------------
# Form scoring
# ---------------------------------------------------------------------------

def compute_form_score(
    exercise: str,
    landmarks: Dict[str, np.ndarray],
) -> int:
    """Return a 0-100 form score derived from joint angles."""
    try:
        if exercise == "SQUAT":
            knee  = calculate_angle(landmarks["hip"], landmarks["knee"], landmarks["ankle"])
            hip_a = calculate_angle(landmarks["shoulder"], landmarks["hip"], landmarks["knee"])
            knee_score = max(0.0, 100.0 - abs(knee - 90.0) * 1.5)
            hip_score  = max(0.0, 100.0 - abs(hip_a - 80.0) * 1.2)
            return max(0, min(100, int((knee_score + hip_score) / 2.0)))

        if exercise == "PUSH_UP":
            elbow     = calculate_angle(landmarks["shoulder"], landmarks["elbow"], landmarks["wrist"])
            body_diff = (
                abs(landmarks["shoulder"][1] - landmarks["hip"][1])
                + abs(landmarks["hip"][1] - landmarks["ankle"][1])
            )
            elbow_score = max(0.0, 100.0 - abs(elbow - 90.0) * 1.0)
            body_score  = max(0.0, 100.0 - body_diff * 200.0)
            return max(0, min(100, int((elbow_score + body_score) / 2.0)))

        if exercise == "PLANK":
            body_diff = (
                abs(landmarks["shoulder"][1] - landmarks["hip"][1])
                + abs(landmarks["hip"][1] - landmarks["ankle"][1])
            )
            return max(0, min(100, int(100.0 - body_diff * 300.0)))

    except Exception:
        pass
    return 75


# ---------------------------------------------------------------------------
# Calorie estimation
# ---------------------------------------------------------------------------

_MET: Dict[str, float] = {"SQUAT": 5.0, "PUSH_UP": 8.0, "PLANK": 4.0}
_BODY_WEIGHT_KG = 70.0


def estimate_calories(exercise: str, reps: int, duration_seconds: int) -> float:
    """Rough kcal estimate from exercise type, rep count, and session duration."""
    met = _MET.get(exercise, 4.0)
    hours = duration_seconds / 3600.0
    base = met * _BODY_WEIGHT_KG * hours
    rep_bonus = reps * 0.2
    return round(base + rep_bonus, 1)
