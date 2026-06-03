"""Full GymEye system launch file.

Starts (in order):
  1. Gazebo simulation (gym.world)
  2. Spawn TurtleBot3 model into the world (5 s delay)
  3. ROS2-Gazebo topic bridge for camera image and cmd_vel (3 s delay)
  4. Camera bridge node — forwards /camera/image_raw frames to backend (3 s delay)
  5. Camera pose node — pose estimation + rep counting + cmd_vel (3 s delay)
  6. Robot controller — polls backend state and publishes cmd_vel (3 s delay)

Usage:
    source /opt/ros/humble/setup.bash   # or jazzy
    ros2 launch ros2/launch/full_system.launch.py

Optional overrides:
    ros2 launch ros2/launch/full_system.launch.py backend_url:=http://192.168.1.10:8000/analysis
"""
from __future__ import annotations

import os
from pathlib import Path

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    ExecuteProcess,
    TimerAction,
)
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

_WORKSPACE = Path(__file__).resolve().parents[3]
_GAZEBO_WORLDS  = _WORKSPACE / "gazebo" / "worlds"
_GAZEBO_MODELS  = _WORKSPACE / "gazebo" / "models"
_ROS2_DIR       = _WORKSPACE / "ros2"


def generate_launch_description() -> LaunchDescription:
    # ------------------------------------------------------------------
    # Launch arguments
    # ------------------------------------------------------------------
    backend_url_arg = DeclareLaunchArgument(
        "backend_url",
        default_value="http://localhost:8000/analysis",
        description="GymEye backend analysis POST endpoint",
    )
    backend_state_arg = DeclareLaunchArgument(
        "backend_state_url",
        default_value="http://localhost:8000/state",
        description="GymEye backend state GET endpoint",
    )
    backend_frame_arg = DeclareLaunchArgument(
        "backend_frame_url",
        default_value="http://localhost:8000/frame",
        description="GymEye backend frame POST endpoint",
    )
    world_arg = DeclareLaunchArgument(
        "world",
        default_value=str(_GAZEBO_WORLDS / "gym.world"),
        description="Path to the Gazebo world SDF file",
    )
    model_name_arg = DeclareLaunchArgument(
        "model_name",
        default_value="turtlebot3_burger",
        description="Gazebo model name for the robot",
    )

    # ------------------------------------------------------------------
    # 1. Gazebo simulation
    # ------------------------------------------------------------------
    gazebo = ExecuteProcess(
        cmd=["gz", "sim", "-r", LaunchConfiguration("world")],
        additional_env={"GZ_SIM_RESOURCE_PATH": str(_GAZEBO_MODELS)},
        output="screen",
        name="gazebo_sim",
    )

    # ------------------------------------------------------------------
    # 2. Spawn robot (delayed to allow world to load)
    # ------------------------------------------------------------------
    model_sdf = str(_GAZEBO_MODELS / "turtlebot3_burger" / "model.sdf")
    spawn_robot = TimerAction(
        period=5.0,
        actions=[
            ExecuteProcess(
                cmd=[
                    "gz", "service",
                    "-s", "/world/gym_world/create",
                    "--reqtype", "gz.msgs.EntityFactory",
                    "--reptype", "gz.msgs.Boolean",
                    "--req",
                    f'sdf_filename: "{model_sdf}" '
                    'name: "turtlebot3_burger" '
                    "pose {position {x: 0 y: 0 z: 0.01}}",
                ],
                output="screen",
                name="spawn_turtlebot3",
            )
        ],
    )

    # ------------------------------------------------------------------
    # 3. ROS2-Gazebo bridge (camera image + cmd_vel)
    # ------------------------------------------------------------------
    gz_bridge = TimerAction(
        period=3.0,
        actions=[
            Node(
                package="ros_gz_bridge",
                executable="parameter_bridge",
                name="gz_ros_bridge",
                arguments=[
                    "/camera/image_raw@sensor_msgs/msg/Image[gz.msgs.Image",
                    "/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist",
                    "/model/turtlebot3_burger/odometry"
                    "@nav_msgs/msg/Odometry[gz.msgs.Odometry",
                ],
                output="screen",
            )
        ],
    )

    # ------------------------------------------------------------------
    # 4. Camera bridge node (image → backend /frame)
    # ------------------------------------------------------------------
    camera_bridge = TimerAction(
        period=3.0,
        actions=[
            Node(
                package="gym_eye_ros2",
                executable="bridge_node",
                name="camera_bridge",
                output="screen",
                additional_env={
                    "BACKEND_FRAME_URL": LaunchConfiguration("backend_frame_url"),
                    "BRIDGE_MAX_FPS": "10",
                },
            )
        ],
    )

    # ------------------------------------------------------------------
    # 5. Camera pose node (pose estimation + rep counting + cmd_vel)
    # ------------------------------------------------------------------
    camera_pose = TimerAction(
        period=3.0,
        actions=[
            Node(
                package="gym_eye_ros2",
                executable="camera_pose_node",
                name="camera_pose_node",
                output="screen",
                additional_env={
                    "BACKEND_URL": LaunchConfiguration("backend_url"),
                },
            )
        ],
    )

    # ------------------------------------------------------------------
    # 6. Robot controller (backend state → /cmd_vel)
    # ------------------------------------------------------------------
    robot_controller = TimerAction(
        period=3.0,
        actions=[
            Node(
                package="gym_eye_ros2",
                executable="robot_controller",
                name="gym_eye_robot_controller",
                output="screen",
                additional_env={
                    "BACKEND_STATE_URL": LaunchConfiguration("backend_state_url"),
                    "CONTROLLER_HZ": "5",
                },
            )
        ],
    )

    return LaunchDescription([
        backend_url_arg,
        backend_state_arg,
        backend_frame_arg,
        world_arg,
        model_name_arg,
        gazebo,
        spawn_robot,
        gz_bridge,
        camera_bridge,
        camera_pose,
        robot_controller,
    ])
