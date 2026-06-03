"""GymEye — PoseEstimatorNode

Subscribes to webcam frames, runs MediaPipe BlazePose with One-Euro smoothing,
and publishes pose landmarks for downstream analysis.

Topics subscribed:
  /gym_eye/camera/image_raw     sensor_msgs/Image

Topics published:
  /gym_eye/pose/detected        std_msgs/Bool         — person visible
  /gym_eye/pose/visibility      std_msgs/Float32      — avg landmark visibility
  /gym_eye/pose/landmarks_json  std_msgs/String       — JSON array (33 landmarks)
  /gym_eye/status               std_msgs/String       — heartbeat

Parameters:
  model_complexity    int    default 1  (0=lite, 1=full, 2=heavy)
  min_detection_conf  float  default 0.6
  min_tracking_conf   float  default 0.6
  smoother_freq       float  default 20.0

Run:
  python3 ros2/nodes/pose_estimator_node.py
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

# Shared utilities
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "pipeline"))
from pose_utils import LandmarkSmoother

try:
    import cv2
    import numpy as np
    from cv_bridge import CvBridge
except ImportError as exc:
    raise SystemExit("opencv-python / cv_bridge required") from exc

try:
    import mediapipe as mp
except ImportError as exc:
    raise SystemExit("mediapipe required: pip install mediapipe") from exc

try:
    import rclpy
    from rclpy.node import Node
    from sensor_msgs.msg import Image
    from std_msgs.msg import Bool, Float32, String
except Exception as exc:
    raise SystemExit("ROS2 not sourced") from exc


class PoseEstimatorNode(Node):
    """Runs MediaPipe BlazePose on incoming camera frames and publishes landmarks."""

    def __init__(self) -> None:
        super().__init__("pose_estimator")

        complexity  = int(self.declare_parameter("model_complexity",    1).value)
        det_conf    = float(self.declare_parameter("min_detection_conf", 0.6).value)
        track_conf  = float(self.declare_parameter("min_tracking_conf",  0.6).value)
        sm_freq     = float(self.declare_parameter("smoother_freq",      20.0).value)

        self._bridge   = CvBridge()
        self._smoother = LandmarkSmoother(freq=sm_freq)
        self._pose     = mp.solutions.pose.Pose(
            model_complexity=complexity,
            enable_segmentation=False,
            min_detection_confidence=det_conf,
            min_tracking_confidence=track_conf,
        )

        self._frames_in   = 0
        self._frames_pose = 0
        self._start       = time.time()

        # Publishers
        self._pub_detected  = self.create_publisher(Bool,    "/gym_eye/pose/detected",       10)
        self._pub_visibility = self.create_publisher(Float32, "/gym_eye/pose/visibility",     10)
        self._pub_landmarks = self.create_publisher(String,  "/gym_eye/pose/landmarks_json", 5)
        self._pub_status    = self.create_publisher(String,  "/gym_eye/status",              10)

        # Subscriber
        self._sub_image = self.create_subscription(
            Image, "/gym_eye/camera/image_raw", self._on_image, 5
        )

        self._status_timer = self.create_timer(5.0, self._publish_status)

        self.get_logger().info(
            f"PoseEstimatorNode ready — complexity={complexity}, "
            f"det={det_conf}, track={track_conf}"
        )

    # ------------------------------------------------------------------

    def _on_image(self, msg: Image) -> None:
        self._frames_in += 1

        try:
            frame = self._bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        except Exception as exc:
            self.get_logger().warning(f"cv_bridge conversion failed: {exc}")
            return

        rgb     = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self._pose.process(rgb)

        detected = results.pose_landmarks is not None
        self._pub_detected.publish(Bool(data=detected))

        if not detected:
            self._pub_visibility.publish(Float32(data=0.0))
            return

        self._frames_pose += 1
        smoothed = self._smoother.smooth(results.pose_landmarks.landmark)

        # Average visibility as pose quality metric
        avg_vis = float(sum(lm.visibility for lm in smoothed) / len(smoothed))
        self._pub_visibility.publish(Float32(data=round(avg_vis, 3)))

        # Serialize landmarks to JSON
        lm_list = [
            {
                "x":   round(lm.x, 5),
                "y":   round(lm.y, 5),
                "z":   round(lm.z, 5),
                "vis": round(lm.visibility, 3),
            }
            for lm in smoothed
        ]
        self._pub_landmarks.publish(String(data=json.dumps(lm_list)))

    def _publish_status(self) -> None:
        uptime   = round(time.time() - self._start, 1)
        det_rate = (
            round(self._frames_pose / self._frames_in * 100, 1)
            if self._frames_in > 0 else 0.0
        )
        status = json.dumps({
            "node":        "pose_estimator",
            "frames_in":   self._frames_in,
            "frames_pose": self._frames_pose,
            "detect_pct":  det_rate,
            "uptime":      uptime,
        })
        self._pub_status.publish(String(data=status))

    def destroy_node(self) -> None:
        self._pose.close()
        super().destroy_node()


def main() -> None:
    rclpy.init()
    node = PoseEstimatorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
