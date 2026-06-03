# Gazebo Assets

This folder contains world files for the demo simulation. Update gym.world as you add props or more realistic scenes.

## TurtleBot3 model
The TurtleBot3-like model lives under gazebo/models/turtlebot3_burger. Set the resource path before launching Gazebo:

```bash
export GZ_SIM_RESOURCE_PATH=$PWD/gazebo/models
```

## GymBot adapter
The adapter polls the backend state and moves the gymbot model in Gazebo. It also reports the robot pose back to the web app.

Run it after Gazebo is open:

```bash
python3 gymbot_adapter.py
```

If the set_pose service name differs, override it:

```bash
GZ_SET_POSE_SERVICE=/world/gym_world/set_pose python3 gymbot_adapter.py
```
