# ROS 2 Bridge

This folder includes a ROS 2 launch file that starts Gazebo Sim and bridges the camera topic into ROS 2.

## Launch

```bash
ros2 launch ros2/gz_sim_bridge.launch.py
```

If ROS 2 can't find the launch file, run it directly:

```bash
python3 ros2/launch/gz_sim_bridge.launch.py
```

## Camera topic
The camera publishes on the gz topic `/camera`, which is bridged to ROS as `/camera`.

Check ROS 2 topic list:

```bash
ros2 topic list
```

## Camera pose node (MediaPipe)

This node subscribes to `/camera`, streams frames to the backend `/frame` endpoint,
and (if MediaPipe is installed) posts pose updates to `/update`.

Dependencies:

```bash
sudo apt install -y ros-jazzy-cv-bridge
```

```bash
pip install mediapipe opencv-python numpy requests
```

Run:

```bash
python3 ros2/camera_pose_node.py
```
