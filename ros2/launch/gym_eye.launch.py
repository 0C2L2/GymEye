"""GymEye full ROS2 system launch file (no Gazebo).

Launches all 6 nodes in order:
  1. webcam_capture      — reads camera → /gym_eye/camera/image_raw
  2. pose_estimator      — MediaPipe → /gym_eye/pose/*
    3. pose_marker         — pose JSON → RViz markers
    4. exercise_analyzer   — classification + reps → /gym_eye/exercise/* + /gym_eye/reps/*
    5. robot_controller    — exercise → /cmd_vel
    6. backend_bridge      — analysis JSON + frames → FastAPI backend

Usage:
  source /opt/ros/jazzy/setup.bash
  python3 ros2/launch/gym_eye.launch.py        # direct
  ros2 launch ros2/launch/gym_eye.launch.py    # via colcon package

Override examples:
  ros2 launch ros2/launch/gym_eye.launch.py camera_index:=1 target_reps:=12
  ros2 launch ros2/launch/gym_eye.launch.py backend_url:=http://192.168.1.5:8000/analysis
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
    # ----------------------------------------------------------------
    # Launch arguments
    # ----------------------------------------------------------------
    args = [
        DeclareLaunchArgument("camera_index",       default_value="0",
                              description="Webcam device index"),
        DeclareLaunchArgument("capture_fps",        default_value="15.0",
                              description="Frame capture rate"),
        DeclareLaunchArgument("model_complexity",   default_value="1",
                              description="MediaPipe model complexity (0/1/2)"),
        DeclareLaunchArgument("target_reps",        default_value="15",
                              description="Target reps per set"),
        DeclareLaunchArgument("linear_speed",       default_value="0.15",
                              description="Robot forward/backward speed m/s"),
        DeclareLaunchArgument("turn_speed",         default_value="0.4",
                              description="Robot rotation speed rad/s"),
        DeclareLaunchArgument("backend_url",        default_value="http://localhost:8000/analysis",
                              description="FastAPI backend analysis endpoint"),
        DeclareLaunchArgument("backend_frame_url",  default_value="http://localhost:8000/frame",
                              description="FastAPI backend frame endpoint"),
    ]

    # ----------------------------------------------------------------
    # 1. Webcam capture
    # ----------------------------------------------------------------
    webcam = Node(
        executable="python3",
        arguments=[_script("webcam_capture_node.py")],
        name="webcam_capture",
        output="screen",
        parameters=[{
            "camera_index": LaunchConfiguration("camera_index"),
            "fps":          LaunchConfiguration("capture_fps"),
        }],
    )

    # ----------------------------------------------------------------
    # 2. Pose estimator (slight delay to let capture start)
    # ----------------------------------------------------------------
    pose = TimerAction(period=1.0, actions=[
        Node(
            executable="python3",
            arguments=[_script("pose_estimator_node.py")],
            name="pose_estimator",
            output="screen",
            parameters=[{
                "model_complexity": LaunchConfiguration("model_complexity"),
            }],
        )
    ])

    # ----------------------------------------------------------------
    # 3. Pose marker (RViz)
    # ----------------------------------------------------------------
    marker = TimerAction(period=2.0, actions=[
        Node(
            executable="python3",
            arguments=[_script("pose_marker_node.py")],
            name="pose_marker",
            output="screen",
        )
    ])

    # ----------------------------------------------------------------
    # 4. Exercise analyzer
    # ----------------------------------------------------------------
    analyzer = TimerAction(period=2.5, actions=[
        Node(
            executable="python3",
            arguments=[_script("exercise_analyzer_node.py")],
            name="exercise_analyzer",
            output="screen",
            parameters=[{
                "target_reps": LaunchConfiguration("target_reps"),
            }],
        )
    ])

    # ----------------------------------------------------------------
    # 5. Robot controller
    # ----------------------------------------------------------------
    robot = TimerAction(period=3.0, actions=[
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

    # ----------------------------------------------------------------
    # 6. Backend bridge
    # ----------------------------------------------------------------
    bridge = TimerAction(period=3.0, actions=[
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

    return LaunchDescription([*args, webcam, pose, marker, analyzer, robot, bridge])
