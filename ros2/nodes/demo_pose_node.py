"""GymEye — DemoPoseNode

Publishes a synthetic pose + camera image for demos without hardware.

Topics published:
  /gym_eye/camera/image_raw     sensor_msgs/Image
  /gym_eye/pose/landmarks_json  std_msgs/String
  /gym_eye/pose/detected        std_msgs/Bool
  /gym_eye/pose/visibility      std_msgs/Float32
  /gym_eye/status               std_msgs/String

Parameters:
  fps            float  default 15.0
  width          int    default 640
  height         int    default 480
  frame_id       str    default camera_frame

Run:
  python3 ros2/nodes/demo_pose_node.py
"""
from __future__ import annotations

import json
import math
import time
from typing import List

try:
    import cv2
    import numpy as np
    from cv_bridge import CvBridge
except ImportError as exc:
    raise SystemExit("opencv-python / cv_bridge required") from exc

try:
    import rclpy
    from rclpy.node import Node
    from sensor_msgs.msg import Image
    from std_msgs.msg import Bool, Float32, String
except Exception as exc:
    raise SystemExit("ROS2 not sourced") from exc


POSE_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 7),
    (0, 4), (4, 5), (5, 6), (6, 8),
    (9, 10),
    (11, 12), (11, 13), (13, 15), (15, 17), (15, 19), (15, 21),
    (12, 14), (14, 16), (16, 18), (16, 20), (16, 22),
    (11, 23), (12, 24), (23, 24),
    (23, 25), (24, 26), (25, 27), (26, 28),
    (27, 29), (28, 30), (29, 31), (30, 32),
]


class DemoPoseNode(Node):
    """Publishes animated synthetic pose landmarks and a demo image."""

    def __init__(self) -> None:
        super().__init__("demo_pose")

        self._fps = float(self.declare_parameter("fps", 15.0).value)
        self._w   = int(self.declare_parameter("width", 640).value)
        self._h   = int(self.declare_parameter("height", 480).value)
        self._frame_id = str(self.declare_parameter("frame_id", "camera_frame").value)

        self._bridge = CvBridge()
        self._start = time.time()
        self._frame = 0

        self._pub_img = self.create_publisher(Image,  "/gym_eye/camera/image_raw", 5)
        self._pub_lm  = self.create_publisher(String, "/gym_eye/pose/landmarks_json", 5)
        self._pub_det = self.create_publisher(Bool,   "/gym_eye/pose/detected", 10)
        self._pub_vis = self.create_publisher(Float32,"/gym_eye/pose/visibility", 10)
        self._pub_status = self.create_publisher(String, "/gym_eye/status", 10)

        self._timer = self.create_timer(1.0 / self._fps, self._tick)
        self._status_timer = self.create_timer(5.0, self._publish_status)

        self.get_logger().info("DemoPoseNode ready — synthetic pose streaming")

    # ------------------------------------------------------------------

    def _base_landmarks(self) -> List[dict]:
        # Start with neutral centered landmarks
        base = [{"x": 0.5, "y": 0.5, "z": 0.0, "vis": 1.0} for _ in range(33)]
        return base

    def _apply_vertical_pose(self, lm: List[dict], t: float) -> None:
        # Squat: vertical body, knee moves forward/back to change angle
        phase = (math.sin(t * 2.0) + 1.0) / 2.0
        hip_y = 0.55 + 0.10 * phase
        knee_y = 0.78 + 0.02 * phase
        knee_offset = 0.12 * phase

        # Head + torso
        lm[0].update(x=0.5, y=0.18)
        lm[11].update(x=0.46, y=0.32)  # left shoulder
        lm[12].update(x=0.54, y=0.32)  # right shoulder
        lm[23].update(x=0.46, y=hip_y) # left hip
        lm[24].update(x=0.54, y=hip_y) # right hip

        # Arms (slight swing)
        lm[13].update(x=0.44, y=0.44)
        lm[14].update(x=0.56, y=0.44)
        lm[15].update(x=0.42, y=0.58)
        lm[16].update(x=0.58, y=0.58)

        # Legs (knee forward to create squat angle)
        lm[25].update(x=0.46 + knee_offset, y=knee_y)
        lm[26].update(x=0.54 + knee_offset, y=knee_y)
        lm[27].update(x=0.46, y=0.95)
        lm[28].update(x=0.54, y=0.95)

    def _apply_horizontal_pose(self, lm: List[dict], t: float, push_up: bool) -> None:
        # Plank / push-up: horizontal body
        base_y = 0.55
        elbow_bend = 0.12 if push_up else 0.02
        phase = (math.sin(t * 2.0) + 1.0) / 2.0 if push_up else 0.0

        lm[0].update(x=0.20, y=base_y - 0.05)
        lm[11].update(x=0.35, y=base_y)  # left shoulder
        lm[12].update(x=0.35, y=base_y)  # right shoulder
        lm[23].update(x=0.60, y=base_y)  # left hip
        lm[24].update(x=0.60, y=base_y)  # right hip
        lm[25].update(x=0.78, y=base_y + 0.02)
        lm[26].update(x=0.78, y=base_y + 0.02)
        lm[27].update(x=0.92, y=base_y + 0.03)
        lm[28].update(x=0.92, y=base_y + 0.03)

        # Elbows move down on push-up
        elbow_y = base_y + elbow_bend * phase
        wrist_y = base_y + 0.20 * phase
        lm[13].update(x=0.42, y=elbow_y)
        lm[14].update(x=0.42, y=elbow_y)
        lm[15].update(x=0.50, y=wrist_y)
        lm[16].update(x=0.50, y=wrist_y)

    def _generate_landmarks(self, t: float) -> List[dict]:
        lm = self._base_landmarks()
        cycle = t % 30.0

        if cycle < 12.0:
            self._apply_vertical_pose(lm, t)
        elif cycle < 22.0:
            self._apply_horizontal_pose(lm, t, push_up=True)
        else:
            self._apply_horizontal_pose(lm, t, push_up=False)

        return lm

    def _draw_pose(self, lm: List[dict]) -> np.ndarray:
        img = np.zeros((self._h, self._w, 3), dtype=np.uint8)

        def _px(p):
            return int(p["x"] * self._w), int(p["y"] * self._h)

        # Lines
        for a, b in POSE_CONNECTIONS:
            if a >= len(lm) or b >= len(lm):
                continue
            ax, ay = _px(lm[a])
            bx, by = _px(lm[b])
            cv2.line(img, (ax, ay), (bx, by), (0, 220, 80), 2)

        # Points
        for p in lm:
            x, y = _px(p)
            cv2.circle(img, (x, y), 4, (255, 255, 255), -1)

        label = "SQUAT -> PUSH_UP -> PLANK demo"
        cv2.putText(img, label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                    0.7, (255, 255, 255), 2)
        return img

    def _tick(self) -> None:
        t = time.time() - self._start
        landmarks = self._generate_landmarks(t)
        img = self._draw_pose(landmarks)

        # Publish image
        msg = self._bridge.cv2_to_imgmsg(img, encoding="bgr8")
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = self._frame_id
        self._pub_img.publish(msg)

        # Publish landmarks JSON
        self._pub_lm.publish(String(data=json.dumps(landmarks)))
        self._pub_det.publish(Bool(data=True))
        self._pub_vis.publish(Float32(data=0.85))

        self._frame += 1

    def _publish_status(self) -> None:
        status = json.dumps({
            "node": "demo_pose",
            "frames": self._frame,
            "uptime": round(time.time() - self._start, 1),
        })
        self._pub_status.publish(String(data=status))


def main() -> None:
    rclpy.init()
    node = DemoPoseNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
