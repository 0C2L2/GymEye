# Webcam Pose Pipeline

This pipeline reads webcam frames, runs MediaPipe BlazePose, and pushes live updates to the backend.
It also uploads JPEG frames to the backend `/frame` endpoint for the web UI.

## Setup

```bash
cd pipeline
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python3 webcam_pose.py
```

Update the backend URL inside webcam_pose.py if needed.
