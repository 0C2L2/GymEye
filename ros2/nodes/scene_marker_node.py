"""GymEye — SceneMarkerNode

Publishes simple environment + robot markers for RViz demos.

Topics published:
  /gym_eye/scene/markers  visualization_msgs/MarkerArray

Parameters:
  frame_id        str    default map
  floor_size      float  default 6.0
  wall_height     float  default 1.2
  wall_thickness  float  default 0.08
  robot_height    float  default 0.6
  robot_radius    float  default 0.18
  publish_rate    float  default 1.0
"""
from __future__ import annotations

try:
    import rclpy
    from rclpy.node import Node
    from geometry_msgs.msg import Point
    from visualization_msgs.msg import Marker, MarkerArray
except Exception as exc:
    raise SystemExit("ROS2 not sourced") from exc


class SceneMarkerNode(Node):
    """Publishes a simple demo scene to RViz."""

    def __init__(self) -> None:
        super().__init__("scene_marker")

        self._frame_id = str(self.declare_parameter("frame_id", "map").value)
        self._floor_size = float(self.declare_parameter("floor_size", 6.0).value)
        self._wall_height = float(self.declare_parameter("wall_height", 1.2).value)
        self._wall_thickness = float(self.declare_parameter("wall_thickness", 0.08).value)
        self._robot_height = float(self.declare_parameter("robot_height", 0.6).value)
        self._robot_radius = float(self.declare_parameter("robot_radius", 0.18).value)
        self._publish_rate = float(self.declare_parameter("publish_rate", 1.0).value)

        self._pub = self.create_publisher(MarkerArray, "/gym_eye/scene/markers", 5)
        self._timer = self.create_timer(1.0 / self._publish_rate, self._publish)

        self.get_logger().info("SceneMarkerNode ready — demo environment enabled")

    def _publish(self) -> None:
        header_stamp = self.get_clock().now().to_msg()
        markers = MarkerArray()

        # Floor
        floor = Marker()
        floor.header.frame_id = self._frame_id
        floor.header.stamp = header_stamp
        floor.ns = "scene"
        floor.id = 0
        floor.type = Marker.CUBE
        floor.action = Marker.ADD
        floor.pose.position.x = 0.0
        floor.pose.position.y = 0.0
        floor.pose.position.z = -0.01
        floor.scale.x = self._floor_size
        floor.scale.y = self._floor_size
        floor.scale.z = 0.02
        floor.color.r = 0.18
        floor.color.g = 0.18
        floor.color.b = 0.20
        floor.color.a = 1.0
        markers.markers.append(floor)

        # Walls
        half = self._floor_size / 2.0
        wall_specs = [
            (1, 0.0,  half, self._floor_size, self._wall_thickness),
            (2, 0.0, -half, self._floor_size, self._wall_thickness),
            (3,  half, 0.0, self._wall_thickness, self._floor_size),
            (4, -half, 0.0, self._wall_thickness, self._floor_size),
        ]
        for wall_id, x, y, sx, sy in wall_specs:
            wall = Marker()
            wall.header.frame_id = self._frame_id
            wall.header.stamp = header_stamp
            wall.ns = "scene"
            wall.id = wall_id
            wall.type = Marker.CUBE
            wall.action = Marker.ADD
            wall.pose.position.x = x
            wall.pose.position.y = y
            wall.pose.position.z = self._wall_height / 2.0
            wall.scale.x = sx
            wall.scale.y = sy
            wall.scale.z = self._wall_height
            wall.color.r = 0.25
            wall.color.g = 0.25
            wall.color.b = 0.28
            wall.color.a = 0.9
            markers.markers.append(wall)

        # Robot body
        body = Marker()
        body.header.frame_id = self._frame_id
        body.header.stamp = header_stamp
        body.ns = "robot"
        body.id = 10
        body.type = Marker.CYLINDER
        body.action = Marker.ADD
        body.pose.position.x = 0.0
        body.pose.position.y = 0.0
        body.pose.position.z = self._robot_height / 2.0
        body.scale.x = self._robot_radius * 2.0
        body.scale.y = self._robot_radius * 2.0
        body.scale.z = self._robot_height
        body.color.r = 0.15
        body.color.g = 0.65
        body.color.b = 0.85
        body.color.a = 0.95
        markers.markers.append(body)

        # Robot head
        head = Marker()
        head.header.frame_id = self._frame_id
        head.header.stamp = header_stamp
        head.ns = "robot"
        head.id = 11
        head.type = Marker.SPHERE
        head.action = Marker.ADD
        head.pose.position.x = 0.0
        head.pose.position.y = 0.0
        head.pose.position.z = self._robot_height + 0.14
        head.scale.x = 0.28
        head.scale.y = 0.28
        head.scale.z = 0.28
        head.color.r = 0.95
        head.color.g = 0.85
        head.color.b = 0.20
        head.color.a = 0.95
        markers.markers.append(head)

        # Robot facing arrow
        arrow = Marker()
        arrow.header.frame_id = self._frame_id
        arrow.header.stamp = header_stamp
        arrow.ns = "robot"
        arrow.id = 12
        arrow.type = Marker.ARROW
        arrow.action = Marker.ADD
        arrow.scale.x = 0.05
        arrow.scale.y = 0.10
        arrow.scale.z = 0.15
        start = Point(x=0.0, y=0.0, z=self._robot_height * 0.9)
        end = Point(x=0.6, y=0.0, z=self._robot_height * 0.9)
        arrow.points = [start, end]
        arrow.color.r = 0.20
        arrow.color.g = 0.95
        arrow.color.b = 0.70
        arrow.color.a = 0.95
        markers.markers.append(arrow)

        # Title text
        text = Marker()
        text.header.frame_id = self._frame_id
        text.header.stamp = header_stamp
        text.ns = "scene"
        text.id = 20
        text.type = Marker.TEXT_VIEW_FACING
        text.action = Marker.ADD
        text.pose.position.x = 0.0
        text.pose.position.y = 0.0
        text.pose.position.z = self._wall_height + 0.2
        text.scale.z = 0.22
        text.color.r = 0.95
        text.color.g = 0.95
        text.color.b = 0.95
        text.color.a = 0.95
        text.text = "GymEye Demo"
        markers.markers.append(text)

        self._pub.publish(markers)


def main() -> None:
    rclpy.init()
    node = SceneMarkerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
