"""GymEye — BackendBridgeNode

Subscribes to the full analysis JSON topic and bridges it into the FastAPI
backend via HTTP POST. Also subscribes to camera frames and forwards them
to the backend /frame endpoint.

Topics subscribed:
  /gym_eye/analysis/json       std_msgs/String  — from ExerciseAnalyzerNode
  /gym_eye/camera/image_raw    sensor_msgs/Image — for frame forwarding

Topics published:
  /gym_eye/backend/connected   std_msgs/Bool    — backend reachability
  /gym_eye/backend/latency_ms  std_msgs/Float32 — last POST round-trip ms
  /gym_eye/status              std_msgs/String

Parameters:
  backend_url         str    default http://localhost:8000/analysis
  backend_frame_url   str    default http://localhost:8000/frame
  frame_fps           float  default 5.0   — how often to forward frames
  retry_interval_sec  float  default 3.0   — health re-check when disconnected

Run:
  python3 ros2/nodes/backend_bridge_node.py
"""
from __future__ import annotations

import json
import os
import sys
import time
import threading
from typing import Optional

try:
    import requests
except ImportError as exc:
    raise SystemExit("requests required: pip install requests") from exc

try:
    import cv2
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


class BackendBridgeNode(Node):
    """Forwards ROS2 analysis messages to the GymEye FastAPI backend."""

    def __init__(self) -> None:
        super().__init__("backend_bridge")

        self._backend_url       = self.declare_parameter("backend_url",       "http://localhost:8000/analysis").value
        self._backend_frame_url = self.declare_parameter("backend_frame_url", "http://localhost:8000/frame").value
        self._frame_fps         = float(self.declare_parameter("frame_fps",   5.0).value)
        self._retry_interval    = float(self.declare_parameter("retry_interval_sec", 3.0).value)

        self._bridge         = CvBridge()
        self._connected      = False
        self._last_post_ms   = 0.0
        self._post_count     = 0
        self._post_errors    = 0
        self._last_frame_t   = 0.0
        self._frame_interval = 1.0 / self._frame_fps
        self._start          = time.time()
        self._lock           = threading.Lock()

        # Publishers
        self._pub_connected = self.create_publisher(Bool,    "/gym_eye/backend/connected",  10)
        self._pub_latency   = self.create_publisher(Float32, "/gym_eye/backend/latency_ms", 10)
        self._pub_status    = self.create_publisher(String,  "/gym_eye/status",             10)

        # Subscribers
        self._sub_analysis = self.create_subscription(
            String, "/gym_eye/analysis/json", self._on_analysis, 5
        )
        self._sub_image = self.create_subscription(
            Image, "/gym_eye/camera/image_raw", self._on_image, 5
        )

        # Health check timer
        self._health_timer  = self.create_timer(self._retry_interval, self._check_health)
        self._status_timer  = self.create_timer(5.0, self._publish_status)

        # Initial health check in background
        threading.Thread(target=self._check_health, daemon=True).start()

        self.get_logger().info(
            f"BackendBridgeNode ready — {self._backend_url}"
        )

    # ------------------------------------------------------------------
    # Subscribers
    # ------------------------------------------------------------------

    def _on_analysis(self, msg: String) -> None:
        try:
            payload = json.loads(msg.data)
        except json.JSONDecodeError:
            return

        t0 = time.time()
        try:
            resp = requests.post(self._backend_url, json=payload, timeout=1.0)
            resp.raise_for_status()
            latency_ms = round((time.time() - t0) * 1000, 1)
            with self._lock:
                self._last_post_ms = latency_ms
                self._post_count  += 1
                self._connected    = True
            self._pub_latency.publish(Float32(data=latency_ms))
            self._pub_connected.publish(Bool(data=True))
        except Exception as exc:
            with self._lock:
                self._post_errors += 1
                self._connected    = False
            self._pub_connected.publish(Bool(data=False))
            self.get_logger().warning(f"Backend POST failed: {exc}")

    def _on_image(self, msg: Image) -> None:
        now = time.time()
        if now - self._last_frame_t < self._frame_interval:
            return
        self._last_frame_t = now

        try:
            frame = self._bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
            ok, encoded = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 75])
            if not ok:
                return
            requests.post(
                self._backend_frame_url,
                data=encoded.tobytes(),
                headers={"Content-Type": "image/jpeg"},
                timeout=0.5,
            )
        except Exception:
            pass  # Frame forwarding is best-effort

    # ------------------------------------------------------------------
    # Health check
    # ------------------------------------------------------------------

    def _check_health(self) -> None:
        url = self._backend_url.replace("/analysis", "/health")
        try:
            resp = requests.get(url, timeout=1.0)
            ok   = resp.status_code == 200
        except Exception:
            ok = False

        with self._lock:
            self._connected = ok

        self._pub_connected.publish(Bool(data=ok))
        if not ok:
            self.get_logger().warning(f"Backend unreachable: {url}")

    # ------------------------------------------------------------------
    # Status heartbeat
    # ------------------------------------------------------------------

    def _publish_status(self) -> None:
        with self._lock:
            connected = self._connected
            count     = self._post_count
            errors    = self._post_errors
            latency   = self._last_post_ms

        status = json.dumps({
            "node":       "backend_bridge",
            "connected":  connected,
            "posts":      count,
            "errors":     errors,
            "latency_ms": latency,
            "uptime":     round(time.time() - self._start, 1),
        })
        self._pub_status.publish(String(data=status))


# ---------------------------------------------------------------------------

def main() -> None:
    rclpy.init()
    node = BackendBridgeNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
