"""GymEye — RobotControllerNode

Subscribes to the current exercise name and drives a robot via /cmd_vel.

Exercise → motion mapping
  SQUAT   → move forward        (linear.x = +speed)
  PUSH_UP → move backward       (linear.x = -speed)
  PLANK   → rotate in place     (angular.z = +turn_speed)
  UNKNOWN → full stop

Also subscribes to rep events and pulses the robot on each completed rep
(brief speed burst) to visually indicate rep count.

Topics subscribed:
  /gym_eye/exercise/name    std_msgs/String
  /gym_eye/reps/total       std_msgs/Int32    — triggers rep pulse
  /gym_eye/feedback         std_msgs/String

Topics published:
  /cmd_vel                  geometry_msgs/Twist
  /gym_eye/robot/state      std_msgs/String   — JSON robot state
  /gym_eye/status           std_msgs/String

Parameters:
  linear_speed   float  default 0.15
  turn_speed     float  default 0.4
  rep_pulse_sec  float  default 0.3   — duration of rep burst
  stop_delay_sec float  default 2.0   — stop robot if no exercise for this long

Run:
  python3 ros2/nodes/robot_controller_node.py
"""
from __future__ import annotations

import json
import time
from typing import Optional

try:
    import rclpy
    from geometry_msgs.msg import Twist
    from rclpy.node import Node
    from std_msgs.msg import Int32, String
except Exception as exc:
    raise SystemExit("ROS2 not sourced") from exc


class RobotControllerNode(Node):
    """Translates exercise state into /cmd_vel robot motion."""

    def __init__(self) -> None:
        super().__init__("robot_controller")

        self._linear_speed  = float(self.declare_parameter("linear_speed",   0.15).value)
        self._turn_speed    = float(self.declare_parameter("turn_speed",      0.40).value)
        self._rep_pulse_sec = float(self.declare_parameter("rep_pulse_sec",   0.30).value)
        self._stop_delay    = float(self.declare_parameter("stop_delay_sec",  2.0).value)

        self._current_exercise = "UNKNOWN"
        self._last_seen        = time.time()
        self._last_rep_count   = 0
        self._pulse_until: Optional[float] = None
        self._start            = time.time()
        self._cmd_count        = 0

        # Publishers
        self._pub_cmd    = self.create_publisher(Twist,  "/cmd_vel",               10)
        self._pub_state  = self.create_publisher(String, "/gym_eye/robot/state",   10)
        self._pub_status = self.create_publisher(String, "/gym_eye/status",        10)

        # Subscribers
        self._sub_name = self.create_subscription(
            String, "/gym_eye/exercise/name", self._on_exercise, 10
        )
        self._sub_reps = self.create_subscription(
            Int32, "/gym_eye/reps/total", self._on_reps, 10
        )
        self._sub_feedback = self.create_subscription(
            String, "/gym_eye/feedback", self._on_feedback, 10
        )

        # Control loop at 20 Hz
        self._control_timer = self.create_timer(0.05, self._control_loop)
        self._status_timer  = self.create_timer(5.0,  self._publish_status)

        self.get_logger().info(
            f"RobotControllerNode ready — "
            f"linear={self._linear_speed} m/s, turn={self._turn_speed} rad/s"
        )

    # ------------------------------------------------------------------
    # Subscribers
    # ------------------------------------------------------------------

    def _on_exercise(self, msg: String) -> None:
        exercise = msg.data.upper().strip()
        if exercise != self._current_exercise:
            self.get_logger().info(f"Exercise: {self._current_exercise} → {exercise}")
            self._current_exercise = exercise
        self._last_seen = time.time()

    def _on_reps(self, msg: Int32) -> None:
        count = msg.data
        if count > self._last_rep_count:
            # New rep completed — trigger a pulse
            self._pulse_until = time.time() + self._rep_pulse_sec
            self.get_logger().info(f"Rep {count} completed — pulse triggered")
        self._last_rep_count = count

    def _on_feedback(self, msg: String) -> None:
        # Log feedback for visibility in rqt_console
        if msg.data:
            self.get_logger().info(f"Feedback: {msg.data}")

    # ------------------------------------------------------------------
    # Control loop
    # ------------------------------------------------------------------

    def _control_loop(self) -> None:
        twist    = Twist()
        now      = time.time()
        exercise = self._current_exercise
        stale    = (now - self._last_seen) > self._stop_delay

        if stale:
            exercise = "UNKNOWN"

        # Rep pulse: boost speed briefly on each new rep
        in_pulse = self._pulse_until is not None and now < self._pulse_until
        multiplier = 2.0 if in_pulse else 1.0

        if exercise == "SQUAT":
            twist.linear.x  = self._linear_speed * multiplier
            twist.angular.z = 0.0
        elif exercise == "PUSH_UP":
            twist.linear.x  = -self._linear_speed * multiplier
            twist.angular.z = 0.0
        elif exercise == "PLANK":
            twist.linear.x  = 0.0
            twist.angular.z = self._turn_speed * multiplier
        else:
            # UNKNOWN or stale — stop
            twist.linear.x  = 0.0
            twist.angular.z = 0.0

        self._pub_cmd.publish(twist)
        self._cmd_count += 1

        # Publish robot state JSON for rqt_topic inspection
        state = json.dumps({
            "exercise":   exercise,
            "linear_x":  round(twist.linear.x,  3),
            "angular_z": round(twist.angular.z, 3),
            "in_pulse":  in_pulse,
            "reps":      self._last_rep_count,
            "stale":     stale,
        })
        self._pub_state.publish(String(data=state))

    # ------------------------------------------------------------------
    # Status heartbeat
    # ------------------------------------------------------------------

    def _publish_status(self) -> None:
        status = json.dumps({
            "node":     "robot_controller",
            "exercise": self._current_exercise,
            "reps":     self._last_rep_count,
            "cmd_sent": self._cmd_count,
            "uptime":   round(time.time() - self._start, 1),
        })
        self._pub_status.publish(String(data=status))


# ---------------------------------------------------------------------------

def main() -> None:
    rclpy.init()
    node = RobotControllerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        # Send stop command before shutting down
        stop = Twist()
        node._pub_cmd.publish(stop)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
