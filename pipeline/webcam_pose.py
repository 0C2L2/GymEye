from __future__ import annotations

import math
import time
from dataclasses import dataclass
from typing import Dict, Optional

import cv2
import mediapipe as mp
import numpy as np
import requests


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


def post_update(url: str, payload: dict) -> None:
    try:
        requests.post(url, json=payload, timeout=0.5)
    except requests.RequestException:
        pass


def post_frame(url: str, frame: np.ndarray) -> None:
    try:
        ok, encoded = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
        if not ok:
            return
        requests.post(url, data=encoded.tobytes(), timeout=0.5, headers={"Content-Type": "image/jpeg"})
    except requests.RequestException:
        pass


def main() -> None:
    backend_url = "http://localhost:8000/analysis"
    backend_frame = "http://localhost:8000/frame"
    cap = cv2.VideoCapture(0)
    pose = mp.solutions.pose.Pose(model_complexity=1, enable_segmentation=False)
    state = PoseState()
    last_frame = 0.0

    while True:
        ok, frame = cap.read()
        if not ok:
            time.sleep(0.1)
            continue

        now = time.time()
        if now - last_frame > 0.2:
            post_frame(backend_frame, frame)
            last_frame = now

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb)

        if results.pose_landmarks:
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
            feedback = update_reps(exercise, landmarks, state)
            knee_angle = calculate_angle(landmarks["hip"], landmarks["knee"], landmarks["ankle"])

            payload = {
                "timestamp": time.time(),
                "exercise": exercise,
                "rep_count": state.reps,
                "form_score": 85 if feedback == "Good depth" else 70 if feedback else 78,
                "feedback": feedback,
                "angles": {"right_knee": knee_angle},
                "source": "browser_ai",
            }
            post_update(backend_url, payload)

        time.sleep(0.05)


if __name__ == "__main__":
    main()
