"""GymEye RViz launch file.

Opens RViz2 with the GymEye visualization config.

Usage:
  source /opt/ros/jazzy/setup.bash
  ros2 launch ros2/launch/rviz_gym.launch.py
  # or
  python3 ros2/launch/rviz_gym.launch.py
"""
from __future__ import annotations

from pathlib import Path

from launch import LaunchDescription
from launch.actions import ExecuteProcess


def generate_launch_description() -> LaunchDescription:
    config = str(Path(__file__).resolve().parents[1] / "rviz" / "gym_eye.rviz")
    rviz = ExecuteProcess(
        cmd=["rviz2", "-d", config],
        output="screen",
        name="rviz2",
    )
    return LaunchDescription([rviz])
