# Gazebo + Raspberry Pi Demo Plan

## Goal
Build a demo where a simulated TurtleBot in Gazebo (3D) runs the perception pipeline (camera + pose estimation) and connects to the existing web app to show live feedback and session data. This replaces missing hardware with simulation while keeping the user experience intact.

## Assumptions
- Available hardware: Raspberry Pi + camera.
- No physical robot hardware or LIDAR.
- Web app already shows pose overlay, rep counting, and session history.
- ROS 2 is acceptable for the demo and Gazebo is used for 3D robot simulation.

## System Overview
- Gazebo: 3D robot simulation, publishes camera frames and robot pose.
- ROS 2: bridges Gazebo topics and provides a node that forwards video frames to the perception pipeline.
- Perception pipeline: MediaPipe BlazePose + One-Euro filter + rep counting.
- Web app: receives live metrics via a lightweight backend (WebSocket or REST).
- Raspberry Pi: runs the perception pipeline and backend service.

## Plan (Phases)

### Phase 1: Confirm software baseline (1-2 days)
- Choose simulation stack: Gazebo + ROS 2 Humble.
- Select a TurtleBot model compatible with Gazebo.
- Validate Raspberry Pi OS and Python environment.
- Decide where MediaPipe runs (Pi or dev PC). For a stable demo, run MediaPipe on the Pi only if performance is acceptable.

### Phase 2: Gazebo simulation setup (2-3 days)
- Create a minimal Gazebo world with a simple gym-like scene (floor + a few static obstacles).
- Spawn the TurtleBot model with a camera sensor.
- Ensure camera topic publishes frames at a stable FPS (20-30 FPS).
- Create a ROS 2 launch file that brings up Gazebo and the robot.

### Phase 3: ROS 2 camera bridge (2-3 days)
- Build a ROS 2 node that subscribes to the Gazebo camera topic and outputs frames in a format the perception pipeline can consume.
- Add a simple frame-rate limiter to avoid CPU overload.
- Expose a test endpoint for local validation (save a frame or show a preview).

### Phase 4: Perception pipeline integration (3-5 days)
- Connect camera frames from ROS 2 to the existing MediaPipe pipeline.
- Apply One-Euro filtering and rep-counting logic.
- Output a consistent JSON schema for the web app (exercise, reps, joint angles, feedback).

### Phase 5: Web app connectivity (2-4 days)
- Add a lightweight backend service on the Pi that streams updates to the web app (WebSocket preferred).
- Implement a dev mode that accepts simulated data if needed.
- Show live status: exercise label, rep count, feedback, and session timer.

### Phase 6: Demo narrative and reliability (2-3 days)
- Script a short demo flow: start Gazebo, start perception, open web app, show live updates.
- Record a short screen capture of the Gazebo simulation + web app UI.
- Add a fallback mode: if the pipeline fails, serve pre-recorded session data.

## Deliverables
- Gazebo world + TurtleBot launch files.
- ROS 2 camera bridge node.
- Perception pipeline running on Raspberry Pi.
- Backend service for web app updates.
- Web app demo mode and instructions.

## Milestones
- M1: Gazebo world launches with camera topic publishing.
- M2: ROS 2 node delivers frames to the perception pipeline.
- M3: Web app receives live JSON updates.
- M4: End-to-end demo recorded.

## Risks and Mitigations
- Pi performance: use lower resolution (640x480) and 20 FPS cap.
- MediaPipe on Pi: if slow, move inference to dev PC and keep the Pi for backend only.
- Gazebo overhead: run Gazebo on dev PC, stream frames to Pi over LAN.

## Next Actions
1. Confirm the exact web app interface for live data (WebSocket or REST).
2. Decide where Gazebo runs (Pi vs dev PC).
3. Pick the TurtleBot model and ROS 2 distribution.
