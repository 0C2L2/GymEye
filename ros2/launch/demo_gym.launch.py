"""GymEye demo launch file (no camera required).

Launches:
  - DemoPoseNode (synthetic pose + image)
  - PoseMarkerNode (RViz markers)
  - ExerciseAnalyzerNode
  - RobotControllerNode
  - BackendBridgeNode
  - Static transform publisher (map -> camera_frame)

Usage:
  source /opt/ros/jazzy/setup.bash
  ros2 launch ros2/launch/demo_gym.launch.py
"""
from __future__ import annotations

from pathlib import Path

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, TimerAction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

_NODES_DIR = str(Path(__file__).resolve().parents[1] / "nodes")


def _script(name: str) -> str:
    return str(Path(_NODES_DIR) / name)


def generate_launch_description() -> LaunchDescription:
    args = [
        DeclareLaunchArgument("demo_fps",       default_value="15.0", description="Demo pose FPS"),
        DeclareLaunchArgument("demo_width",     default_value="640",  description="Demo image width"),
        DeclareLaunchArgument("demo_height",    default_value="480",  description="Demo image height"),
        DeclareLaunchArgument("target_reps",    default_value="15",   description="Target reps"),
        DeclareLaunchArgument("linear_speed",   default_value="0.15", description="Robot speed"),
        DeclareLaunchArgument("turn_speed",     default_value="0.4",  description="Robot turn speed"),
        DeclareLaunchArgument("backend_url",    default_value="http://localhost:8000/analysis",
                              description="FastAPI backend analysis endpoint"),
        DeclareLaunchArgument("backend_frame_url", default_value="http://localhost:8000/frame",
                              description="FastAPI backend frame endpoint"),
    ]

    # Static transform to keep RViz happy
    static_tf = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        name="static_tf_camera",
        arguments=["0", "0", "0", "0", "0", "0", "map", "camera_frame"],
        output="screen",
    )

    demo_pose = Node(
        executable="python3",
        arguments=[_script("demo_pose_node.py")],
        name="demo_pose",
        output="screen",
        parameters=[{
            "fps":   LaunchConfiguration("demo_fps"),
            "width": LaunchConfiguration("demo_width"),
            "height": LaunchConfiguration("demo_height"),
        }],
    )

    marker = TimerAction(period=1.0, actions=[
        Node(
            executable="python3",
            arguments=[_script("pose_marker_node.py")],
            name="pose_marker",
            output="screen",
        )
    ])

    scene_marker_node = Node(
        executable="python3",
        arguments=[_script("scene_marker_node.py")],
        name="scene_marker",
        output="screen",
    )

    analyzer = TimerAction(period=1.5, actions=[
        Node(
            executable="python3",
            arguments=[_script("exercise_analyzer_node.py")],
            name="exercise_analyzer",
            output="screen",
            parameters=[{"target_reps": LaunchConfiguration("target_reps")}],
        )
    ])

    robot = TimerAction(period=2.0, actions=[
        Node(
            executable="python3",
            arguments=[_script("robot_controller_node.py")],
            name="robot_controller",
            output="screen",
            parameters=[{
                "linear_speed": LaunchConfiguration("linear_speed"),
                "turn_speed":   LaunchConfiguration("turn_speed"),
            }],
        )
    ])

    bridge = TimerAction(period=2.0, actions=[
        Node(
            executable="python3",
            arguments=[_script("backend_bridge_node.py")],
            name="backend_bridge",
            output="screen",
            parameters=[{
                "backend_url":       LaunchConfiguration("backend_url"),
                "backend_frame_url": LaunchConfiguration("backend_frame_url"),
            }],
        )
    ])

    return LaunchDescription([
        *args,
        static_tf,
        demo_pose,
        marker,
        scene_marker_node,
        analyzer,
        robot,
        bridge,
    ])
