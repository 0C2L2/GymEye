"""DEPRECATED — use ros2/nodes/backend_bridge_node.py instead."""
import os, sys
from pathlib import Path
new = Path(__file__).parent / "nodes" / "backend_bridge_node.py"
os.execv(sys.executable, [sys.executable, str(new)] + sys.argv[1:])
if False:
    pass


def main() -> None:
    try:
        import rclpy
        from rclpy.node import Node
        from sensor_msgs.msg import Image
    except Exception as exc:
        raise SystemExit(
            "rclpy or ROS 2 messages are not installed. "
            "Install ROS 2 Humble and source the setup before running."
        ) from exc

    try:
        import cv2
        import requests
        from cv_bridge import CvBridge
    except Exception as exc:
        raise SystemExit(
            "Missing dependencies. Install: ros-humble-cv-bridge opencv-python requests"
        ) from exc

    import time

    BACKEND_FRAME_URL = os.getenv("BACKEND_FRAME_URL", "http://localhost:8000/frame")
    MAX_FPS = float(os.getenv("BRIDGE_MAX_FPS", "10"))
    FRAME_INTERVAL = 1.0 / MAX_FPS

    class CameraBridge(Node):
        def __init__(self) -> None:
            super().__init__("camera_bridge")
            self._bridge = CvBridge()
            self._last_sent = 0.0
            self._lock = threading.Lock()
            self.subscription = self.create_subscription(
                Image,
                "/camera/image_raw",
                self._on_image,
                10,
            )
            self.get_logger().info(
                f"CameraBridge ready — forwarding to {BACKEND_FRAME_URL} at {MAX_FPS} FPS"
            )

        def _on_image(self, msg: Image) -> None:
            now = time.time()
            with self._lock:
                if now - self._last_sent < FRAME_INTERVAL:
                    return
                self._last_sent = now

            try:
                frame = self._bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
            except Exception as exc:
                self.get_logger().warning(f"cv_bridge conversion failed: {exc}")
                return

            ok, encoded = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
            if not ok:
                return

            try:
                requests.post(
                    BACKEND_FRAME_URL,
                    data=encoded.tobytes(),
                    headers={"Content-Type": "image/jpeg"},
                    timeout=0.3,
                )
            except requests.RequestException:
                pass

    rclpy.init()
    node = CameraBridge()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
