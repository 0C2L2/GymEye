"""GymEye — WebcamCaptureNode

Reads the system webcam and publishes frames as sensor_msgs/Image.

Topics published:
  /gym_eye/camera/image_raw   sensor_msgs/Image   — raw BGR frames
  /gym_eye/status             std_msgs/String     — JSON status heartbeat

Parameters:
  camera_index  int    default 0      — V4L2 device index
  fps           float  default 15.0   — publish rate (capture always at 30)
  width         int    default 640
  height        int    default 480

Run:
  python3 ros2/nodes/webcam_capture_node.py
"""
from __future__ import annotations

import json
import numpy as np
import os
import sys
import time
from pathlib import Path

try:
    import cv2
except ImportError as exc:
    raise SystemExit("opencv-python required: pip install opencv-python") from exc

try:
    import rclpy
    from cv_bridge import CvBridge
    from rclpy.node import Node
    from sensor_msgs.msg import Image
    from std_msgs.msg import String
except Exception as exc:
    raise SystemExit(
        "ROS2 not sourced or cv_bridge missing.\n"
        "source /opt/ros/jazzy/setup.bash && pip install opencv-python"
    ) from exc


class WebcamCaptureNode(Node):
    """Publishes webcam frames on /gym_eye/camera/image_raw."""

    def __init__(self) -> None:
        super().__init__("webcam_capture")

        cam   = int(self.declare_parameter("camera_index", 0).value)
        fps   = float(self.declare_parameter("fps", 15.0).value)
        w     = int(self.declare_parameter("width", 640).value)
        h     = int(self.declare_parameter("height", 480).value)

        self._bridge     = CvBridge()
        self._frame_num  = 0
        self._dropped    = 0
        self._start      = time.time()

        self._pub_img    = self.create_publisher(Image,  "/gym_eye/camera/image_raw", 5)
        self._pub_status = self.create_publisher(String, "/gym_eye/status",           10)

        self._cap = cv2.VideoCapture(cam)
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH,  w)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
        self._cap.set(cv2.CAP_PROP_FPS, 30)

        self._synthetic = False
        if not self._cap.isOpened():
            self.get_logger().warning(
                f"Camera {cam} not available — using synthetic test pattern"
            )
            self._cap = None
            self._synthetic = True

        self._timer        = self.create_timer(1.0 / fps,  self._capture)
        self._status_timer = self.create_timer(5.0,         self._publish_status)

        mode = "SYNTHETIC" if self._synthetic else f"camera {cam}"
        self.get_logger().info(
            f"WebcamCaptureNode ready — {mode}, {w}x{h} @ {fps} FPS"
        )

    # ------------------------------------------------------------------

    def _make_synthetic_frame(self) -> "cv2.Mat":
        import numpy as np
        h = int(self.get_parameter("height").value)
        w = int(self.get_parameter("width").value)
        frame = np.zeros((h, w, 3), dtype=np.uint8)
        # animated bar so the frame changes each tick
        bar_x = int((self._frame_num * 4) % w)
        frame[:, bar_x : bar_x + 8] = (0, 200, 80)
        cv2.putText(frame, f"SYNTHETIC #{self._frame_num}",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        return frame

    def _capture(self) -> None:
        if self._synthetic:
            frame = self._make_synthetic_frame()
            ok = True
        else:
            ok, frame = self._cap.read()
        if not ok:
            self._dropped += 1
            self.get_logger().warning(
                f"Webcam read failed (dropped={self._dropped})"
            )
            return

        try:
            msg             = self._bridge.cv2_to_imgmsg(frame, encoding="bgr8")
            msg.header.stamp = self.get_clock().now().to_msg()
            msg.header.frame_id = "camera_frame"
            self._pub_img.publish(msg)
            self._frame_num += 1
        except Exception as exc:
            self.get_logger().error(f"Frame publish error: {exc}")

    def _publish_status(self) -> None:
        uptime = round(time.time() - self._start, 1)
        status = json.dumps({
            "node":    "webcam_capture",
            "frames":  self._frame_num,
            "dropped": self._dropped,
            "uptime":  uptime,
        })
        self._pub_status.publish(String(data=status))

    def destroy_node(self) -> None:
        if self._cap is not None:
            self._cap.release()
        super().destroy_node()


def main() -> None:
    rclpy.init()
    node = WebcamCaptureNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
