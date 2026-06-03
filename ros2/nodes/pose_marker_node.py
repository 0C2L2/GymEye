"""GymEye — PoseMarkerNode

Subscribes to JSON pose landmarks and publishes RViz markers.

Topics subscribed:
  /gym_eye/pose/landmarks_json  std_msgs/String

Topics published:
  /gym_eye/pose/markers         visualization_msgs/MarkerArray
  /gym_eye/status               std_msgs/String

Parameters:
  frame_id         str    default camera_frame
  point_scale      float  default 0.05
  line_width       float  default 0.01
  position_scale   float  default 2.0
  min_visibility   float  default 0.3

Run:
  python3 ros2/nodes/pose_marker_node.py
"""
from __future__ import annotations

import json
import time

try:
    import rclpy
    from rclpy.node import Node
    from std_msgs.msg import String
    from geometry_msgs.msg import Point
    from visualization_msgs.msg import Marker, MarkerArray
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

LEFT_IDXS = {1, 2, 3, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31}
RIGHT_IDXS = {4, 5, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32}


class PoseMarkerNode(Node):
    """Publishes RViz markers from pose landmark JSON."""

    def __init__(self) -> None:
        super().__init__("pose_marker")

        self._frame_id       = str(self.declare_parameter("frame_id", "camera_frame").value)
        self._point_scale    = float(self.declare_parameter("point_scale", 0.05).value)
        self._line_width     = float(self.declare_parameter("line_width", 0.01).value)
        self._pos_scale      = float(self.declare_parameter("position_scale", 2.0).value)
        self._min_vis        = float(self.declare_parameter("min_visibility", 0.3).value)

        self._pub_markers = self.create_publisher(MarkerArray, "/gym_eye/pose/markers", 5)
        self._pub_status  = self.create_publisher(String, "/gym_eye/status", 10)
        self._sub_lm = self.create_subscription(
            String, "/gym_eye/pose/landmarks_json", self._on_landmarks, 5
        )

        self._last_publish = 0.0
        self._start = time.time()

        self.get_logger().info("PoseMarkerNode ready — RViz markers enabled")

    # ------------------------------------------------------------------

    def _to_point(self, lm: dict) -> Point:
        p = Point()
        p.x = (lm.get("x", 0.5) - 0.5) * self._pos_scale
        p.y = -(lm.get("y", 0.5) - 0.5) * self._pos_scale
        p.z = -lm.get("z", 0.0) * self._pos_scale
        return p

    def _color_for_idx(self, idx: int) -> tuple[float, float, float]:
        if idx in LEFT_IDXS:
            return (0.1, 0.6, 1.0)
        if idx in RIGHT_IDXS:
            return (1.0, 0.4, 0.1)
        return (0.9, 0.9, 0.9)

    def _on_landmarks(self, msg: String) -> None:
        try:
            landmarks = json.loads(msg.data)
        except json.JSONDecodeError:
            return

        if not isinstance(landmarks, list) or len(landmarks) < 33:
            return

        now = time.time()
        self._last_publish = now

        marker_array = MarkerArray()
        header_stamp = self.get_clock().now().to_msg()

        # Skeleton line list
        line = Marker()
        line.header.frame_id = self._frame_id
        line.header.stamp = header_stamp
        line.ns = "pose"
        line.id = 0
        line.type = Marker.LINE_LIST
        line.action = Marker.ADD
        line.scale.x = self._line_width
        line.color.r = 0.2
        line.color.g = 0.9
        line.color.b = 0.2
        line.color.a = 0.8

        for a, b in POSE_CONNECTIONS:
            if a >= len(landmarks) or b >= len(landmarks):
                continue
            if landmarks[a].get("vis", 1.0) < self._min_vis:
                continue
            if landmarks[b].get("vis", 1.0) < self._min_vis:
                continue
            line.points.append(self._to_point(landmarks[a]))
            line.points.append(self._to_point(landmarks[b]))

        marker_array.markers.append(line)

        # Individual landmark spheres
        for idx, lm in enumerate(landmarks):
            if lm.get("vis", 1.0) < self._min_vis:
                continue
            sphere = Marker()
            sphere.header.frame_id = self._frame_id
            sphere.header.stamp = header_stamp
            sphere.ns = "pose_points"
            sphere.id = idx + 1
            sphere.type = Marker.SPHERE
            sphere.action = Marker.ADD
            sphere.pose.position = self._to_point(lm)
            sphere.scale.x = self._point_scale
            sphere.scale.y = self._point_scale
            sphere.scale.z = self._point_scale
            r, g, b = self._color_for_idx(idx)
            sphere.color.r = r
            sphere.color.g = g
            sphere.color.b = b
            sphere.color.a = 0.9
            marker_array.markers.append(sphere)

        self._pub_markers.publish(marker_array)

    def _publish_status(self) -> None:
        status = json.dumps({
            "node": "pose_marker",
            "last_publish_sec": round(time.time() - self._last_publish, 2),
            "uptime": round(time.time() - self._start, 1),
        })
        self._pub_status.publish(String(data=status))


def main() -> None:
    rclpy.init()
    node = PoseMarkerNode()
    timer = node.create_timer(5.0, node._publish_status)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        timer.cancel()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
