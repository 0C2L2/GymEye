"""DEPRECATED — use ros2/nodes/pose_estimator_node.py + ros2/nodes/exercise_analyzer_node.py instead."""
import os, sys
from pathlib import Path
new = Path(__file__).parent / "nodes" / "pose_estimator_node.py"
os.execv(sys.executable, [sys.executable, str(new)] + sys.argv[1:])
from pathlib import Path

# Import shared utilities from the pipeline directory
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "pipeline"))

import requests

try:
    import cv2
    import numpy as np
    from cv_bridge import CvBridge
except Exception as exc:
    raise SystemExit(
        "Missing dependencies. Install: ros-humble-cv-bridge opencv-python numpy."
    ) from exc

try:
    import mediapipe as mp
except Exception as exc:
    raise SystemExit("mediapipe not installed. Run: pip install mediapipe") from exc

try:
    import rclpy
    from geometry_msgs.msg import Twist
    from rclpy.node import Node
    from sensor_msgs.msg import Image
except Exception as exc:
    raise SystemExit("ROS 2 is not installed or not sourced.") from exc

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

# Movement commands per exercise: (linear_x m/s, angular_z rad/s)
_EXERCISE_CMD: dict[str, tuple[float, float]] = {
    "SQUAT":   (0.15, 0.0),
    "PUSH_UP": (-0.10, 0.0),
    "PLANK":   (0.0, 0.4),
    "UNKNOWN": (0.0, 0.0),
}


class CameraPoseNode(Node):
    """ROS2 node: subscribes to camera images, runs pose estimation,
    publishes cmd_vel robot motion, and posts analysis to the backend."""

    def __init__(self) -> None:
        super().__init__("camera_pose_node")
        self._backend_url = os.getenv("BACKEND_URL", "http://localhost:8000/analysis")
        self._bridge = CvBridge()
        self._pose = mp.solutions.pose.Pose(
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6,
        )
        self._smoother = LandmarkSmoother(freq=20.0)
        self._state = RepState()
        self._exercise_history: list[str] = []
        self._last_post = 0.0

        self._image_sub = self.create_subscription(
            Image, "/camera/image_raw", self._on_image, 10
        )
        self._cmd_vel_pub = self.create_publisher(Twist, "/cmd_vel", 10)
        self.get_logger().info("CameraPoseNode started.")

    def _on_image(self, msg: Image) -> None:
        try:
            frame = self._bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        except Exception as exc:
            self.get_logger().warning(f"Image conversion failed: {exc}")
            return

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self._pose.process(rgb)

        if not results.pose_landmarks:
            return

        smoothed  = self._smoother.smooth(results.pose_landmarks.landmark)
        landmarks = extract_landmarks(smoothed)
        exercise  = classify_exercise(landmarks)

        self._exercise_history.append(exercise)
        if len(self._exercise_history) > 10:
            self._exercise_history.pop(0)

        stable = max(set(self._exercise_history), key=self._exercise_history.count)

        if stable != self._state.exercise:
            self._state = RepState()
            self._state.exercise = stable

        feedback   = update_reps(stable, landmarks, self._state)
        form_score = compute_form_score(stable, landmarks)
        now        = time.time()
        duration   = int(now - _START_TIME)
        calories   = estimate_calories(stable, self._state.reps, duration)

        self._publish_cmd_vel(stable)

        if now - self._last_post > 0.1:
            self._last_post = now
            knee_angle = round(
                calculate_angle(landmarks["hip"], landmarks["knee"], landmarks["ankle"]), 1
            )
            elbow_angle = round(
                calculate_angle(landmarks["shoulder"], landmarks["elbow"], landmarks["wrist"]), 1
            )
            payload = {
                "source": "raspberry_pi",
                "exercise": stable,
                "completedReps": self._state.reps,
                "correctReps": self._state.correct_reps,
                "incorrectReps": self._state.incorrect_reps,
                "formScore": form_score,
                "activeSuggestion": feedback or None,
                "durationSeconds": duration,
                "caloriesEstimate": calories,
                "cameraActive": True,
                "personDetected": True,
                "bodyVisible": "full",
                "confidence": 0.85,
                "repResults": self._state.rep_results[-20:],
                "angles": {
                    "rightKnee": knee_angle,
                    "rightElbow": elbow_angle,
                },
                "timestamp": now,
            }
            try:
                requests.post(self._backend_url, json=payload, timeout=0.3)
            except requests.RequestException:
                pass

    def _publish_cmd_vel(self, exercise: str) -> None:
        linear_x, angular_z = _EXERCISE_CMD.get(exercise, (0.0, 0.0))
        twist = Twist()
        twist.linear.x = linear_x
        twist.angular.z = angular_z
        self._cmd_vel_pub.publish(twist)


def main() -> None:
    rclpy.init()
    node = CameraPoseNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()

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
