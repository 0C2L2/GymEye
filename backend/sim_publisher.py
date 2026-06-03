from __future__ import annotations

import json
import time
import urllib.request


def send_update(url: str, payload: dict) -> None:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=5) as resp:
        resp.read()


def main() -> None:
    url = "http://localhost:8000/analysis"
    exercises = ["SQUAT", "PUSH_UP", "PLANK"]
    rep_count = 0
    idx = 0

    while True:
        rep_count += 1
        if rep_count % 5 == 0:
            idx = (idx + 1) % len(exercises)

        payload = {
            "exercise": exercises[idx],
            "rep_count": rep_count,
            "form_score": 82 if exercises[idx] == "SQUAT" else 78,
            "feedback": "Keep it steady",
            "angles": {"knee": 110.0, "hip": 95.0, "elbow": 124.0},
            "robot_pose": {"x": 0.2 * idx, "y": 0.1 * (rep_count % 5)},
            "mistakes": [],
            "source": "gazebo",
        }
        send_update(url, payload)
        time.sleep(1)


if __name__ == "__main__":
    main()
