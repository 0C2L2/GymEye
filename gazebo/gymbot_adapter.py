"""GymEye Gazebo adapter.

Reads the live exercise state from the GymEye backend and:
  1. Moves the TurtleBot3 in Gazebo via the gz CLI (always).
  2. Publishes geometry_msgs/Twist on /cmd_vel via ROS2 (when available).

Exercise → robot behaviour
  SQUAT   : advance forward on Y axis + forward cmd_vel
  PUSH_UP : retreat on Y axis + backward cmd_vel
  PLANK   : drift on X axis + rotate cmd_vel
  UNKNOWN : drift back toward origin, stop

Environment variables:
    BACKEND_STATE_URL     default: http://localhost:8000/state
    BACKEND_UPDATE_URL    default: http://localhost:8000/analysis
    GZ_SET_POSE_SERVICE   default: /world/gym_world/set_pose
    GZ_MODEL_NAME         default: turtlebot3_burger
    USE_ROS2              default: auto  (auto | true | false)
"""
from __future__ import annotations

import math
import os
import subprocess
import sys
import time
from typing import Dict, Optional, Tuple

import requests


# ---------------------------------------------------------------------------
# Backend helpers
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Gazebo gz CLI pose control
# ---------------------------------------------------------------------------

def yaw_to_quat(yaw: float) -> Dict[str, float]:
    return {
        "x": 0.0,
        "y": 0.0,
        "z": math.sin(yaw / 2.0),
        "w": math.cos(yaw / 2.0),
    }


def set_pose_gz(
    service: str,
    name: str,
    x: float,
    y: float,
    z: float,
    yaw: float,
) -> None:
    quat = yaw_to_quat(yaw)
    req = (
        f'name: "{name}" '
        f"position {{x: {x} y: {y} z: {z}}} "
        f'orientation {{x: {quat["x"]} y: {quat["y"]} z: {quat["z"]} w: {quat["w"]}}}'
    )
    cmd = [
        "gz", "service", "-s", service,
        "--reqtype", "gz.msgs.Pose",
        "--reptype", "gz.msgs.Boolean",
        "--req", req,
    ]
    subprocess.run(cmd, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


# ---------------------------------------------------------------------------
# ROS2 cmd_vel (loaded at runtime — graceful if ROS2 is absent)
# ---------------------------------------------------------------------------

# Exercise → (linear_x m/s, angular_z rad/s)
_EXERCISE_CMD: Dict[str, Tuple[float, float]] = {
    "SQUAT":   (0.15,  0.0),
    "PUSH_UP": (-0.10, 0.0),
    "PLANK":   (0.0,   0.4),
    "UNKNOWN": (0.0,   0.0),
}

_ros2_node = None
_rclpy = None


def _init_ros2() -> bool:
    global _ros2_node, _rclpy
    try:
        import rclpy
        from geometry_msgs.msg import Twist
        from rclpy.node import Node

        if not rclpy.ok():
            rclpy.init()

        class _CmdVelNode(Node):
            def __init__(self) -> None:
                super().__init__("gymbot_adapter")
                self._pub = self.create_publisher(Twist, "/cmd_vel", 10)

            def publish(self, linear_x: float, angular_z: float) -> None:
                msg = Twist()
                msg.linear.x  = linear_x
                msg.angular.z = angular_z
                self._pub.publish(msg)

        _ros2_node = _CmdVelNode()
        _rclpy = rclpy
        return True
    except Exception:
        return False


def _publish_cmd_vel(exercise: str) -> None:
    if _ros2_node is None:
        return
    try:
        linear_x, angular_z = _EXERCISE_CMD.get(exercise, (0.0, 0.0))
        _ros2_node.publish(linear_x, angular_z)
        _rclpy.spin_once(_ros2_node, timeout_sec=0.0)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def main() -> None:
    backend_state  = os.getenv("BACKEND_STATE_URL",  "http://localhost:8000/state")
    backend_update = os.getenv("BACKEND_UPDATE_URL", "http://localhost:8000/analysis")
    service        = os.getenv("GZ_SET_POSE_SERVICE", "/world/gym_world/set_pose")
    model_name     = os.getenv("GZ_MODEL_NAME", "turtlebot3_burger")
    use_ros2_env   = os.getenv("USE_ROS2", "auto").lower()

    ros2_available = False
    if use_ros2_env in ("auto", "true", "1", "yes"):
        ros2_available = _init_ros2()
        if ros2_available:
            print("[gymbot_adapter] ROS2 cmd_vel enabled on /cmd_vel")
        else:
            print("[gymbot_adapter] ROS2 not available — using gz service only")

    x, y, yaw = 0.0, 0.0, 0.0
    step      = 0.05
    yaw_step  = 0.1

    while True:
        state    = get_state(backend_state)
        analysis = state.get("analysis", state)
        exercise = str(analysis.get("exercise") or "UNKNOWN").upper()

        # --- ROS2 cmd_vel (when available) ---
        if ros2_available:
            _publish_cmd_vel(exercise)

        # --- Gazebo pose update (always) ---
        if exercise == "SQUAT":
            y   += step
            yaw  = 0.0
        elif exercise == "PUSH_UP":
            y   -= step
            yaw  = 0.0
        elif exercise == "PLANK":
            x   += step
            yaw += yaw_step
        else:
            # Gently drift back toward origin
            x   *= 0.98
            y   *= 0.98
            yaw *= 0.95

        # Clamp within gym world bounds
        x   = max(-4.0, min(4.0, x))
        y   = max(-4.0, min(4.0, y))
        yaw = yaw % (2.0 * math.pi)

        set_pose_gz(service, model_name, x, y, 0.0, yaw)
        send_robot_pose(
            backend_update,
            {"x": round(x, 3), "y": round(y, 3), "yaw": round(yaw, 3)},
        )

        time.sleep(0.1)


if __name__ == "__main__":
    main()
