from __future__ import annotations

import sys


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

    class CameraBridge(Node):
        def __init__(self) -> None:
            super().__init__("camera_bridge")
            self.subscription = self.create_subscription(
                Image,
                "/camera/image_raw",
                self.on_image,
                10,
            )

        def on_image(self, msg: Image) -> None:
            # TODO: Convert Image to a frame and forward to the perception pipeline.
            pass

    rclpy.init()
    node = CameraBridge()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
