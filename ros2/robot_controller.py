"""DEPRECATED — use ros2/nodes/robot_controller_node.py instead."""
import os, sys
from pathlib import Path
new = Path(__file__).parent / "nodes" / "robot_controller_node.py"
os.execv(sys.executable, [sys.executable, str(new)] + sys.argv[1:])
if False:
    pass  # unused but prevents empty module

Exercise → robot behaviour
  SQUAT   : move forward (simulate approaching the squat rack)
  PUSH_UP : move backward (simulate backing away)
  PLANK   : rotate in place (stand-by spin)
  UNKNOWN : stop

Usage (after sourcing ROS2):
    python3 ros2/robot_controller.py

Environment variables:
    BACKEND_STATE_URL   default: http://localhost:8000/state
    CONTROLLER_HZ       default: 5  (polls per second)
"""
from __future__ import annotations

import os
import sys

try:
    import requests
except ImportError as exc:
    raise SystemExit("requests not installed. Run: pip install requests") from exc

try:
    import rclpy
    from geometry_msgs.msg import Twist
    from rclpy.node import Node
except Exception as exc:
    raise SystemExit("ROS 2 is not installed or not sourced.") from exc


# ---------------------------------------------------------------------------
# Exercise → (linear_x m/s, angular_z rad/s)
# ---------------------------------------------------------------------------
_EXERCISE_CMD: dict[str, tuple[float, float]] = {
    "SQUAT":   (0.15,  0.0),
    "PUSH_UP": (-0.10, 0.0),
    "PLANK":   (0.0,   0.4),
    "UNKNOWN": (0.0,   0.0),
}


class RobotController(Node):
    """Polls the GymEye backend and drives the robot based on exercise state."""

    def __init__(self) -> None:
        super().__init__("gym_eye_robot_controller")

        self._backend_state_url = os.getenv(
            "BACKEND_STATE_URL", "http://localhost:8000/state"
        )
        self._poll_hz = float(os.getenv("CONTROLLER_HZ", "5"))
        self._last_exercise = "UNKNOWN"

        self._cmd_pub = self.create_publisher(Twist, "/cmd_vel", 10)
        self._timer   = self.create_timer(1.0 / self._poll_hz, self._poll_and_drive)

        self.get_logger().info(
            f"RobotController polling {self._backend_state_url} at {self._poll_hz} Hz"
        )

    def _poll_and_drive(self) -> None:
        exercise = self._fetch_exercise()
        if exercise != self._last_exercise:
            self.get_logger().info(
                f"Exercise: {self._last_exercise} → {exercise}"
            )
            self._last_exercise = exercise
        self._publish_twist(exercise)

    def _fetch_exercise(self) -> str:
        try:
            resp = requests.get(self._backend_state_url, timeout=0.5)
            data = resp.json()
            analysis = data.get("analysis", {})
            return str(analysis.get("exercise") or "UNKNOWN").upper()
        except Exception:
            return "UNKNOWN"

    def _publish_twist(self, exercise: str) -> None:
        linear_x, angular_z = _EXERCISE_CMD.get(exercise, (0.0, 0.0))
        twist = Twist()
        twist.linear.x  = linear_x
        twist.angular.z = angular_z
        self._cmd_pub.publish(twist)


def main() -> None:
    rclpy.init()
    node = RobotController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
