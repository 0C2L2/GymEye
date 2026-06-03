# Gym Eye Web Dashboard

This `web/` folder is the main Gym Eye frontend inside `project_last_set`.

It is a single connected dashboard, not a separate demo app.

## What it does

The dashboard renders one normalized workout state from multiple sources:

- Demo mode
- Browser AI mode
- Live backend WebSocket updates
- REST `/state` fallback

## Main features

- camera / frame area
- huge rep counter
- active feedback panel
- current exercise and confidence
- form score with sub-scores
- mistake tracking
- rep-by-rep breakdown
- local session history
- integration debug panel

## Run locally

```bash
cd web
python3 -m http.server 5173
```

Open:

```txt
http://localhost:5173
```

## Backend connection

The dashboard expects these backend endpoints:

- WebSocket: `ws://localhost:8000/ws`
- REST: `http://localhost:8000/state`
- Frame stream: `http://localhost:8000/frame`

You can change the URLs in the dashboard UI.

## Mode behavior

### Auto

Priority:

1. WebSocket live backend
2. REST polling
3. Browser AI
4. Demo

### Demo

Mock workout data only.

### Browser AI

Uses browser camera and browser-side exercise logic.
This mode is integrated in code, but it still needs a real browser camera verification pass.

### Live Backend

Uses backend state and backend frame stream.

## Notes

- Browser AI is optional and does not block the rest of the dashboard.
- Session history is stored in browser local storage.
- The debug panel shows raw payloads and normalized state for integration testing.
