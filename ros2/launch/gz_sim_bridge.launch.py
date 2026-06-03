from __future__ import annotations

from pathlib import Path

from launch import LaunchDescription
from launch.actions import SetEnvironmentVariable
from launch.actions import ExecuteProcess


def generate_launch_description() -> LaunchDescription:
    world_path = Path(__file__).resolve().parents[2] / "gazebo" / "worlds" / "gym.world"
    model_path = Path(__file__).resolve().parents[2] / "gazebo" / "models"
    bridge_config = Path(__file__).resolve().parents[1] / "bridge_config.yaml"

    set_resource_path = SetEnvironmentVariable(
        name="GZ_SIM_RESOURCE_PATH",
        value=str(model_path),
    )

    gz_sim = ExecuteProcess(
        cmd=["gz", "sim", str(world_path)],
        output="screen",
    )

    bridge = ExecuteProcess(
        cmd=[
            "ros2",
            "run",
            "ros_gz_bridge",
            "parameter_bridge",
            "--ros-args",
            "-p",
            f"config_file:={bridge_config}",
        ],
        output="screen",
    )

    return LaunchDescription([set_resource_path, gz_sim, bridge])
