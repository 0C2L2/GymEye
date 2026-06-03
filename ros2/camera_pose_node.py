from __future__ import annotations

import math
import os
import time
from dataclasses import dataclass
from typing import Dict, Optional

import requests

try:
    import cv2
    import numpy as np
    from cv_bridge import CvBridge
except Exception as exc:  # pragma: no cover
    raise SystemExit(
        "Missing dependencies. Install: ros-jazzy-cv-bridge, opencv-python, numpy."
    ) from exc

try:
    import mediapipe as mp
except Exception:
    mp = None

try:
    import rclpy
    from rclpy.node import Node
    from sensor_msgs.msg import Image
except Exception as exc:  # pragma: no cover
    raise SystemExit("ROS 2 is not installed or not sourced.") from exc


@dataclass
class PoseState:
    stage: str = "UP"
    reps: int = 0


def calculate_angle(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> float:
    ab = a - b
    cb = c - b
    radians = math.atan2(cb[1], cb[0]) - math.atan2(ab[1], ab[0])
    angle = abs(radians * 180.0 / math.pi)
    return 360.0 - angle if angle > 180.0 else angle


def classify_exercise(landmarks: Dict[str, np.ndarray]) -> str:
    shoulder = landmarks["shoulder"]
    hip = landmarks["hip"]
    ankle = landmarks["ankle"]
    elbow = landmarks["elbow"]

    is_horizontal = abs(shoulder[1] - hip[1]) < 0.15 and abs(hip[1] - ankle[1]) < 0.15
    is_vertical = abs(shoulder[0] - hip[0]) < 0.15 and abs(hip[0] - ankle[0]) < 0.15

    if is_horizontal:
        elbow_angle = calculate_angle(landmarks["shoulder"], elbow, landmarks["wrist"])
        return "PUSH_UP" if elbow_angle < 120 else "PLANK"
    if is_vertical:
        return "SQUAT"
    return "UNKNOWN"


def update_reps(exercise: str, landmarks: Dict[str, np.ndarray], state: PoseState) -> str:
    feedback = ""
    if exercise != "SQUAT":
        return feedback

    knee_angle = calculate_angle(landmarks["hip"], landmarks["knee"], landmarks["ankle"])
    if knee_angle > 165:
        state.stage = "UP"
    if knee_angle < 95 and state.stage == "UP":
        state.stage = "DOWN"
        state.reps += 1
        feedback = "Good depth"
    elif 95 <= knee_angle < 130 and state.stage == "UP":
        feedback = "Go lower"
    return feedback


def post_json(url: str, payload: dict) -> None:
    try:
        requests.post(url, json=payload, timeout=0.5)
    except requests.RequestException:
        pass


def post_frame(url: str, jpg_bytes: bytes) -> None:
    try:
        requests.post(url, data=jpg_bytes, timeout=0.5, headers={"Content-Type": "image/jpeg"})
    except requests.RequestException:
        pass


class CameraPoseNode(Node):
    def __init__(self) -> None:
        super().__init__("camera_pose_node")
        self.bridge = CvBridge()
        self.state = PoseState()
        self.pose = mp.solutions.pose.Pose(model_complexity=1) if mp else None
        self.last_tick = 0.0
        self.frame_interval = 1.0 / float(os.getenv("FRAME_RATE", "10"))
        self.backend_update = os.getenv("BACKEND_UPDATE_URL", "http://localhost:8000/analysis")
        self.backend_frame = os.getenv("BACKEND_FRAME_URL", "http://localhost:8000/frame")
        self.subscription = self.create_subscription(Image, "/camera", self.on_image, 10)

    def on_image(self, msg: Image) -> None:
        now = time.time()
        if now - self.last_tick < self.frame_interval:
            return
        self.last_tick = now

        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        ok, encoded = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
        if ok:
            post_frame(self.backend_frame, encoded.tobytes())

        if not self.pose:
            return

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb)
        if not results.pose_landmarks:
            return

        lm = results.pose_landmarks.landmark
        landmarks = {
            "shoulder": np.array([lm[12].x, lm[12].y]),
            "hip": np.array([lm[24].x, lm[24].y]),
            "ankle": np.array([lm[28].x, lm[28].y]),
            "knee": np.array([lm[26].x, lm[26].y]),
            "elbow": np.array([lm[14].x, lm[14].y]),
            "wrist": np.array([lm[16].x, lm[16].y]),
        }
        exercise = classify_exercise(landmarks)
        feedback = update_reps(exercise, landmarks, self.state)
        knee_angle = calculate_angle(landmarks["hip"], landmarks["knee"], landmarks["ankle"])

        payload = {
            "timestamp": time.time(),
            "exercise": exercise,
            "rep_count": self.state.reps,
            "form_score": 85 if feedback == "Good depth" else 70 if feedback else 78,
            "feedback": feedback,
            "angles": {"right_knee": knee_angle},
            "source": "browser_ai",
        }
        post_json(self.backend_update, payload)


def main() -> None:
    rclpy.init()
    node = CameraPoseNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
