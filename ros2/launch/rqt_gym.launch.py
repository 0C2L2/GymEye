"""GymEye rqt launch file.

Opens rqt with a pre-configured perspective that shows:
  - rqt_graph   : full node/topic graph
  - rqt_plot    : form_score + reps + joint angles live plots
  - rqt_topic   : topic list + message inspector
  - rqt_console : live log output from all nodes

Usage:
  source /opt/ros/jazzy/setup.bash
  python3 ros2/launch/rqt_gym.launch.py
  # or
  ros2 launch ros2/launch/rqt_gym.launch.py
"""
from __future__ import annotations

from pathlib import Path

from launch import LaunchDescription
from launch.actions import ExecuteProcess


def generate_launch_description() -> LaunchDescription:
    perspective_file = str(
        Path(__file__).resolve().parent / "gym_eye_rqt.perspective"
    )

    # If a saved perspective exists, use it; otherwise open plain rqt
    if Path(perspective_file).exists():
        rqt = ExecuteProcess(
            cmd=["rqt", "--perspective-file", perspective_file],
            output="screen",
            name="rqt",
        )
    else:
        rqt = ExecuteProcess(
            cmd=[
                "rqt",
                "--standalone", "rqt_plot",
                "--args",
                "/gym_eye/exercise/form_score/data",
                "/gym_eye/reps/total/data",
                "/gym_eye/reps/correct/data",
                "/gym_eye/angles/right_knee/data",
                "/gym_eye/angles/right_elbow/data",
                "/gym_eye/exercise/calories/data",
            ],
            output="screen",
            name="rqt_plot",
        )

    return LaunchDescription([rqt])
