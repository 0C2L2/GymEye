from __future__ import annotations

import os
import sys
import time
from pathlib import Path

# Allow importing shared utilities from this directory
sys.path.insert(0, str(Path(__file__).parent))

import cv2
import mediapipe as mp
import numpy as np
import requests

from pose_utils import (
    LandmarkSmoother,
    RepState,
    calculate_angle,
    classify_exercise,
    compute_form_score,
    estimate_calories,
    extract_landmarks,
    update_reps,
)

_START_TIME = time.time()


def post_json(url: str, payload: dict) -> None:
    try:
        requests.post(url, json=payload, timeout=0.5)
    except requests.RequestException:
        pass


def post_frame(url: str, frame: np.ndarray) -> None:
    try:
        ok, encoded = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
        if not ok:
            return
        requests.post(
            url,
            data=encoded.tobytes(),
            timeout=0.5,
            headers={"Content-Type": "image/jpeg"},
        )
    except requests.RequestException:
        pass


def main() -> None:
    backend_url = os.getenv("BACKEND_URL", "http://localhost:8000/analysis")
    backend_frame_url = os.getenv("BACKEND_FRAME_URL", "http://localhost:8000/frame")
    camera_index = int(os.getenv("CAMERA_INDEX", "0"))

    cap = cv2.VideoCapture(camera_index)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)

    pose = mp.solutions.pose.Pose(
        model_complexity=1,
        enable_segmentation=False,
        min_detection_confidence=0.6,
        min_tracking_confidence=0.6,
    )

    smoother = LandmarkSmoother(freq=20.0)
    state = RepState()
    exercise_history: list[str] = []
    last_frame_post = 0.0
    last_update_post = 0.0

    while True:
        ok, frame = cap.read()
        if not ok:
            time.sleep(0.05)
            continue

        now = time.time()

        # Post raw frame to backend at ~5 FPS
        if now - last_frame_post > 0.2:
            post_frame(backend_frame_url, frame)
            last_frame_post = now

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb)

        if results.pose_landmarks:
            smoothed = smoother.smooth(results.pose_landmarks.landmark)
            landmarks = extract_landmarks(smoothed)
            exercise = classify_exercise(landmarks)

            exercise_history.append(exercise)
            if len(exercise_history) > 10:
                exercise_history.pop(0)

            # Majority vote over last 10 frames for stable classification
            stable_exercise = max(set(exercise_history), key=exercise_history.count)

            # Reset rep state when exercise changes
            if stable_exercise != state.exercise:
                state = RepState()
                state.exercise = stable_exercise

            feedback = update_reps(stable_exercise, landmarks, state)
            form_score = compute_form_score(stable_exercise, landmarks)
            duration = int(now - _START_TIME)
            calories = estimate_calories(stable_exercise, state.reps, duration)

            knee_angle = round(
                calculate_angle(landmarks["hip"], landmarks["knee"], landmarks["ankle"]), 1
            )
            elbow_angle = round(
                calculate_angle(landmarks["shoulder"], landmarks["elbow"], landmarks["wrist"]), 1
            )

            if now - last_update_post > 0.1:
                payload = {
                    "source": "raspberry_pi",
                    "exercise": stable_exercise,
                    "completedReps": state.reps,
                    "correctReps": state.correct_reps,
                    "incorrectReps": state.incorrect_reps,
                    "formScore": form_score,
                    "activeSuggestion": feedback or None,
                    "durationSeconds": duration,
                    "caloriesEstimate": calories,
                    "cameraActive": True,
                    "personDetected": True,
                    "bodyVisible": "full",
                    "confidence": 0.85,
                    "repResults": state.rep_results[-20:],
                    "angles": {
                        "rightKnee": knee_angle,
                        "rightElbow": elbow_angle,
                    },
                    "timestamp": now,
                }
                post_json(backend_url, payload)
                last_update_post = now

        time.sleep(0.03)


if __name__ == "__main__":
    main()
