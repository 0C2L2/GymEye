"""GymEye — ExerciseAnalyzerNode

Subscribes to pose landmarks, runs exercise classification, rep counting,
form scoring, and publishes individual metric topics (all plottable in rqt_plot).

Topics subscribed:
  /gym_eye/pose/landmarks_json  std_msgs/String  — JSON landmarks from PoseEstimatorNode
  /gym_eye/pose/detected        std_msgs/Bool

Topics published (individual metrics — all visible in rqt_plot):
  /gym_eye/exercise/name          std_msgs/String
  /gym_eye/exercise/form_score    std_msgs/Float32
  /gym_eye/exercise/confidence    std_msgs/Float32
  /gym_eye/exercise/calories      std_msgs/Float32
  /gym_eye/exercise/duration_sec  std_msgs/Int32
  /gym_eye/reps/total             std_msgs/Int32
  /gym_eye/reps/correct           std_msgs/Int32
  /gym_eye/reps/incorrect         std_msgs/Int32
  /gym_eye/reps/last_score        std_msgs/Float32
  /gym_eye/reps/target            std_msgs/Int32
  /gym_eye/feedback               std_msgs/String
  /gym_eye/angles/right_knee      std_msgs/Float32
  /gym_eye/angles/left_knee       std_msgs/Float32
  /gym_eye/angles/right_elbow     std_msgs/Float32
  /gym_eye/angles/left_elbow      std_msgs/Float32
  /gym_eye/angles/right_hip       std_msgs/Float32
  /gym_eye/angles/left_hip        std_msgs/Float32
  /gym_eye/analysis/json          std_msgs/String  — full GymEyeAnalysis JSON
  /gym_eye/status                 std_msgs/String

Parameters:
  target_reps  int  default 15

Run:
  python3 ros2/nodes/exercise_analyzer_node.py
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "pipeline"))
from pose_utils import (
    RepState,
    calculate_angle,
    classify_exercise,
    compute_form_score,
    estimate_calories,
    extract_landmarks,
    update_reps,
)

try:
    import rclpy
    from rclpy.node import Node
    from std_msgs.msg import Bool, Float32, Int32, String
except Exception as exc:
    raise SystemExit("ROS2 not sourced") from exc


class ExerciseAnalyzerNode(Node):
    """Core analytics node: classifies exercise, counts reps, scores form."""

    def __init__(self) -> None:
        super().__init__("exercise_analyzer")

        self._target_reps = int(self.declare_parameter("target_reps", 15).value)

        # Internal state
        self._state            = RepState()
        self._exercise_history: List[str] = []
        self._start_time       = time.time()
        self._last_detected    = False
        self._last_feedback    = ""
        self._last_form_score  = 75
        self._last_exercise    = "UNKNOWN"
        self._frames_analyzed  = 0

        # ---- Publishers -----------------------------------------------
        def _pub(msg_type, topic: str, qos: int = 10):
            return self.create_publisher(msg_type, topic, qos)

        self._pub_name         = _pub(String,  "/gym_eye/exercise/name")
        self._pub_form_score   = _pub(Float32, "/gym_eye/exercise/form_score")
        self._pub_confidence   = _pub(Float32, "/gym_eye/exercise/confidence")
        self._pub_calories     = _pub(Float32, "/gym_eye/exercise/calories")
        self._pub_duration     = _pub(Int32,   "/gym_eye/exercise/duration_sec")
        self._pub_reps_total   = _pub(Int32,   "/gym_eye/reps/total")
        self._pub_reps_correct = _pub(Int32,   "/gym_eye/reps/correct")
        self._pub_reps_incorrect = _pub(Int32, "/gym_eye/reps/incorrect")
        self._pub_reps_score   = _pub(Float32, "/gym_eye/reps/last_score")
        self._pub_reps_target  = _pub(Int32,   "/gym_eye/reps/target")
        self._pub_feedback     = _pub(String,  "/gym_eye/feedback")
        self._pub_angle_rknee  = _pub(Float32, "/gym_eye/angles/right_knee")
        self._pub_angle_lknee  = _pub(Float32, "/gym_eye/angles/left_knee")
        self._pub_angle_relbow = _pub(Float32, "/gym_eye/angles/right_elbow")
        self._pub_angle_lelbow = _pub(Float32, "/gym_eye/angles/left_elbow")
        self._pub_angle_rhip   = _pub(Float32, "/gym_eye/angles/right_hip")
        self._pub_angle_lhip   = _pub(Float32, "/gym_eye/angles/left_hip")
        self._pub_analysis     = _pub(String,  "/gym_eye/analysis/json",     5)
        self._pub_status       = _pub(String,  "/gym_eye/status")

        # ---- Subscribers ----------------------------------------------
        self._sub_landmarks = self.create_subscription(
            String, "/gym_eye/pose/landmarks_json", self._on_landmarks, 5
        )
        self._sub_detected = self.create_subscription(
            Bool, "/gym_eye/pose/detected", self._on_detected, 10
        )

        # Publish target reps once and on a slow timer
        self._pub_reps_target.publish(Int32(data=self._target_reps))
        self._status_timer = self.create_timer(5.0, self._publish_status)

        self.get_logger().info(
            f"ExerciseAnalyzerNode ready — target_reps={self._target_reps}"
        )

    # ------------------------------------------------------------------
    # Subscribers
    # ------------------------------------------------------------------

    def _on_detected(self, msg: Bool) -> None:
        self._last_detected = msg.data

    def _on_landmarks(self, msg: String) -> None:
        try:
            raw = json.loads(msg.data)
        except json.JSONDecodeError:
            return

        if not raw or len(raw) < 29:
            return

        # Rebuild numpy landmarks from JSON
        lm = [_LM(p["x"], p["y"], p["z"], p.get("vis", 1.0)) for p in raw]
        landmarks = extract_landmarks(lm)

        # ---- Classification ------------------------------------------
        exercise = classify_exercise(landmarks)
        self._exercise_history.append(exercise)
        if len(self._exercise_history) > 10:
            self._exercise_history.pop(0)
        stable = max(set(self._exercise_history), key=self._exercise_history.count)

        if stable != self._state.exercise:
            self._state = RepState()
            self._state.exercise = stable

        # ---- Analysis ------------------------------------------------
        feedback   = update_reps(stable, landmarks, self._state)
        form_score = compute_form_score(stable, landmarks)
        now        = time.time()
        duration   = int(now - self._start_time)
        calories   = estimate_calories(stable, self._state.reps, duration)

        if feedback:
            self._last_feedback = feedback
        self._last_form_score = form_score
        self._last_exercise   = stable
        self._frames_analyzed += 1

        # ---- Angle computation ---------------------------------------
        rknee  = _angle(landmarks, "hip",          "knee",         "ankle")
        lknee  = _angle(landmarks, "left_hip",     "left_knee",    "left_ankle")
        relbow = _angle(landmarks, "shoulder",     "elbow",        "wrist")
        lelbow = _angle(landmarks, "left_shoulder","left_elbow",   "left_wrist")
        rhip   = _angle(landmarks, "shoulder",     "hip",          "knee")
        lhip   = _angle(landmarks, "left_shoulder","left_hip",     "left_knee")

        # ---- Publish individual topics --------------------------------
        self._pub_name.publish(String(data=stable))
        self._pub_form_score.publish(Float32(data=float(form_score)))
        self._pub_confidence.publish(Float32(data=0.85))
        self._pub_calories.publish(Float32(data=float(calories)))
        self._pub_duration.publish(Int32(data=duration))
        self._pub_reps_total.publish(Int32(data=self._state.reps))
        self._pub_reps_correct.publish(Int32(data=self._state.correct_reps))
        self._pub_reps_incorrect.publish(Int32(data=self._state.incorrect_reps))
        if self._state.rep_results:
            self._pub_reps_score.publish(
                Float32(data=float(self._state.rep_results[-1]["score"]))
            )
        self._pub_reps_target.publish(Int32(data=self._target_reps))
        self._pub_feedback.publish(String(data=self._last_feedback))
        self._pub_angle_rknee.publish(Float32(data=float(rknee)))
        self._pub_angle_lknee.publish(Float32(data=float(lknee)))
        self._pub_angle_relbow.publish(Float32(data=float(relbow)))
        self._pub_angle_lelbow.publish(Float32(data=float(lelbow)))
        self._pub_angle_rhip.publish(Float32(data=float(rhip)))
        self._pub_angle_lhip.publish(Float32(data=float(lhip)))

        # ---- Full analysis JSON (for backend bridge + rqt_topic) -----
        analysis = {
            "source":           "raspberry_pi",
            "exercise":         stable,
            "cameraActive":     True,
            "personDetected":   self._last_detected,
            "bodyVisible":      "full",
            "completedReps":    self._state.reps,
            "correctReps":      self._state.correct_reps,
            "incorrectReps":    self._state.incorrect_reps,
            "targetReps":       self._target_reps,
            "formScore":        form_score,
            "confidence":       0.85,
            "activeSuggestion": self._last_feedback or None,
            "durationSeconds":  duration,
            "caloriesEstimate": calories,
            "repResults":       self._state.rep_results[-20:],
            "angles": {
                "rightKnee":  round(rknee,  1),
                "leftKnee":   round(lknee,  1),
                "rightElbow": round(relbow, 1),
                "leftElbow":  round(lelbow, 1),
                "rightHip":   round(rhip,   1),
                "leftHip":    round(lhip,   1),
            },
            "timestamp": now,
        }
        self._pub_analysis.publish(String(data=json.dumps(analysis)))

    # ------------------------------------------------------------------
    # Status heartbeat
    # ------------------------------------------------------------------

    def _publish_status(self) -> None:
        status = json.dumps({
            "node":           "exercise_analyzer",
            "exercise":       self._last_exercise,
            "reps":           self._state.reps,
            "form_score":     self._last_form_score,
            "frames_analyzed": self._frames_analyzed,
            "uptime":         round(time.time() - self._start_time, 1),
        })
        self._pub_status.publish(String(data=status))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class _LM:
    """Minimal landmark object compatible with pose_utils.extract_landmarks."""
    __slots__ = ("x", "y", "z", "visibility")

    def __init__(self, x: float, y: float, z: float, visibility: float) -> None:
        self.x = x
        self.y = y
        self.z = z
        self.visibility = visibility


def _angle(
    landmarks: Dict,
    a_key: str,
    b_key: str,
    c_key: str,
) -> float:
    """Safe angle calculation — returns 0.0 if any key is missing."""
    try:
        return round(calculate_angle(landmarks[a_key], landmarks[b_key], landmarks[c_key]), 1)
    except (KeyError, Exception):
        return 0.0


# ---------------------------------------------------------------------------

def main() -> None:
    rclpy.init()
    node = ExerciseAnalyzerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
