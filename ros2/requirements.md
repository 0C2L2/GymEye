# ROS 2 + Gazebo requirements

Install ROS 2 Jazzy and ros_gz packages on Ubuntu 24.04:

```bash
sudo apt update
sudo apt install -y ros-jazzy-desktop ros-jazzy-ros-gz ros-jazzy-gz-sim-vendor
```

Additional ROS 2 dependencies for camera bridging:

```bash
sudo apt install -y ros-jazzy-cv-bridge
```

Python dependencies for pose inference:

```bash
pip install mediapipe opencv-python numpy requests
```

Source ROS 2:

```bash
echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc
source /opt/ros/jazzy/setup.bash
```
