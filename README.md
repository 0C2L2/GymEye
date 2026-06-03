# Gym Eye Integrated System

This repository is now the main **Gym Eye** system. It is not two separate projects pasted together.

`project_last_set` remains the source of truth for the full system structure:

- `backend/` is the live analysis bridge
- `web/` is the connected Gym Eye dashboard
- `pipeline/`, `ros2/`, and `gazebo/` publish exercise state into the backend

Useful GymEye functionality was integrated into this system:

- browser-side pose analysis mode
- exercise detection and rep counting patterns
- One-Euro smoothing
- live form feedback
- rep-by-rep breakdown
- local session history and summary views

## System modes

The web dashboard supports one connected data model across these modes:

| Mode | Description |
|---|---|
| `Demo` | Mock workout state when backend and browser AI are unavailable |
| `Browser AI` | Browser camera + MediaPipe pose analysis |
| `Live Backend` | WebSocket or REST state coming from the FastAPI backend |
| `Auto` | Prefer WebSocket, then REST, then Browser AI, then Demo |

## Shared analysis contract

All sources normalize into one `GymEyeAnalysis` shape in `backend/analysis_contract.py` and `web/modules/normalizeAnalysis.js`.

That means all of these feed the same dashboard:

```txt
Demo mock data
Browser AI results
Legacy backend payloads
Raspberry Pi / pipeline updates
Gazebo / robot pose updates
```

## Backend bridge

The backend keeps the latest normalized analysis state in memory and exposes:

- `GET /health`
- `GET /state`
- `POST /analysis`
- `POST /update` (legacy compatibility)
- `POST /state` (compatibility)
- `POST /frame`
- `GET /frame`
- `GET /ws`

The main integration flow is:

```txt
Camera / Raspberry Pi / Browser Demo
        ↓
Pose + Exercise Analysis
        ↓
Normalized Analysis Payload
        ↓
FastAPI state bridge
        ↓
WebSocket + REST fallback
        ↓
Gym Eye dashboard + history + summary
```

## Quick start

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000
```

### Web dashboard

```bash
cd web
python3 -m http.server 5173
```

Open:

```txt
http://localhost:5173
```

The `web/` dashboard is a static HTML/CSS/JS app. It does not currently use `npm run build` or `npm run lint`.

### Optional simulator publisher

```bash
cd backend
python3 sim_publisher.py
```

### Optional webcam pipeline

```bash
cd pipeline
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 webcam_pose.py
```

### Optional Gazebo adapter

```bash
export GZ_SIM_RESOURCE_PATH=$PWD/gazebo/models
gz sim gazebo/worlds/gym.world
```

In another terminal:

```bash
cd gazebo
python3 gymbot_adapter.py
```

## Testing with curl

You can simulate a Raspberry Pi update with:

```bash
curl -X POST http://localhost:8000/analysis \
  -H "Content-Type: application/json" \
  -d '{
    "exercise": "squat",
    "rep_count": 7,
    "form_score": 78,
    "feedback": "Keep your knees aligned with your toes",
    "mistakes": [
      {
        "label": "Knees caving inward",
        "severity": "medium",
        "suggestion": "Push your knees outward"
      }
    ],
    "source": "raspberry_pi"
  }'
```

Then verify:

- `GET /state`
- live update in the web dashboard
- rep counter, exercise, and feedback refresh without reload

## Frontend behavior

The dashboard now includes:

- live camera or backend frame area
- large rep counter
- active feedback card
- current exercise panel
- form score and sub-scores
- mistake tracking
- rep-by-rep breakdown
- local session history
- integration debug panel

## Browser AI note

Browser AI mode is optional. It uses browser camera access and tries to load MediaPipe pose assets in the browser. If the model runtime is unavailable, the dashboard still works in Demo and Live Backend modes.
The Browser AI runtime was integrated and the browser camera permission flow was verified, but full pose-quality validation still depends on a real human camera session.

## Limitations

- Session history is currently local browser storage only
- Browser AI depends on browser camera permissions and MediaPipe runtime availability
- Browser AI mode has not yet been fully verified with a real browser camera session in this validation pass
- Upstream ROS2, Gazebo, and Raspberry Pi publishers still decide how rich their outgoing payloads are
- No database or user authentication is added in this step

## Key files

- `INTEGRATION_NOTES.md`
- `backend/app.py`
- `backend/analysis_contract.py`
- `web/index.html`
- `web/app.js`
- `web/modules/browserAI.js`
- `web/modules/normalizeAnalysis.js`
