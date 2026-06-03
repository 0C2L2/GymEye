# Gym Eye Integration Notes

## Main source of truth

`project_last_set` remains the main repository and system shell.

- `backend/` stays the central bridge for incoming analysis, latest state, WebSocket broadcast, and frame access.
- `web/` becomes the connected Gym Eye dashboard for demo mode, browser AI mode, and live backend mode.
- `pipeline/`, `ros2/`, and `gazebo/` continue to publish into the backend instead of bypassing it.

## Functionality adopted from GymEye

The following ideas and algorithms are adapted from the GymEye source repository:

- browser-side pose tracking entry point
- joint angle calculation
- exercise classification for squat, push-up, and plank
- repetition counting logic
- One-Euro landmark smoothing
- form feedback patterns
- local session history and session summaries
- modern fitness dashboard presentation patterns

## What stays from project_last_set

The following structure and responsibilities stay in place:

- `backend/` owns the live analysis state and transport
- `gazebo/` can still push robot pose and simulation signals
- `pipeline/` can still send webcam pose updates and frames
- `ros2/` can still act as a ROS2 bridge or camera pose publisher
- `web/` remains the single frontend app served separately from the backend

## Data flow

The final integration uses one normalized analysis shape:

```txt
Raspberry Pi / Pipeline / Gazebo / Browser AI / Demo
        ↓
Normalization layer
        ↓
GymEyeAnalysis
        ↓
FastAPI latest state + WebSocket broadcast + REST fallback
        ↓
Web dashboard state manager
        ↓
Live dashboard + feedback + history + summaries
```

## Implemented modes

The integrated system supports these modes:

- `demo`: fallback mock state when backend and browser AI are unavailable
- `browser_ai`: browser camera + MediaPipe-based pose analysis when started by the user
- `backend`: REST/WebSocket-backed live state from the backend bridge
- `raspberry_pi` and `gazebo`: represented through the normalized `source` field when those publishers send updates through the backend

## Backend compatibility

The backend accepts both:

- already-normalized Gym Eye payloads
- simple legacy payloads such as `rep_count`, `feedback`, and `angles`

Legacy senders are normalized into the shared contract before being stored or broadcast.

## Current limitations

- Browser AI depends on MediaPipe browser assets and may be unavailable without network access to the model runtime.
- Session history is stored locally in browser storage for now.
- No database persistence is added in this integration step.
- Gazebo and ROS2 publishers are kept compatible, but their upstream payload richness still depends on what they currently publish.
