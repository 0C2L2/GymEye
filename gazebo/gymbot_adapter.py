from __future__ import annotations

import json
import math
import os
import subprocess
import time
from typing import Dict

import requests


def get_state(url: str) -> Dict:
    try:
        resp = requests.get(url, timeout=0.5)
        return resp.json()
    except requests.RequestException:
        return {}


def send_robot_pose(url: str, pose: Dict[str, float]) -> None:
    payload = {"robot_pose": pose, "source": "gazebo"}
    try:
        requests.post(url, json=payload, timeout=0.5)
    except requests.RequestException:
        pass


def yaw_to_quat(yaw: float) -> Dict[str, float]:
    return {
        "x": 0.0,
        "y": 0.0,
        "z": math.sin(yaw / 2.0),
        "w": math.cos(yaw / 2.0),
    }


def set_pose(service: str, name: str, x: float, y: float, z: float, yaw: float) -> None:
    quat = yaw_to_quat(yaw)
    req = (
        f'name: "{name}" '
        f'position {{x: {x} y: {y} z: {z}}} '
        f'orientation {{x: {quat["x"]} y: {quat["y"]} z: {quat["z"]} w: {quat["w"]}}}'
    )

    cmd = [
        "gz",
        "service",
        "-s",
        service,
        "--reqtype",
        "gz.msgs.Pose",
        "--reptype",
        "gz.msgs.Boolean",
        "--req",
        req,
    ]
    subprocess.run(cmd, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main() -> None:
    backend_state = os.getenv("BACKEND_STATE_URL", "http://localhost:8000/state")
    backend_update = os.getenv("BACKEND_UPDATE_URL", "http://localhost:8000/analysis")
    service = os.getenv("GZ_SET_POSE_SERVICE", "/world/gym_world/set_pose")
    model_name = os.getenv("GZ_MODEL_NAME", "turtlebot3_burger")

    x, y, yaw = 0.0, 0.0, 0.0
    step = 0.05

    while True:
        state = get_state(backend_state)
        exercise = str(state.get("exercise", "UNKNOWN")).upper()

        if exercise == "SQUAT":
            y += step
        elif exercise == "PUSH_UP":
            y -= step
        elif exercise == "PLANK":
            x += step
        else:
            x -= step

        x = max(-2.5, min(2.5, x))
        y = max(-2.5, min(2.5, y))
        yaw += 0.03

        set_pose(service, model_name, x, y, 0.1, yaw)
        send_robot_pose(backend_update, {"x": x, "y": y, "yaw": yaw})
        time.sleep(0.2)


if __name__ == "__main__":
    main()
