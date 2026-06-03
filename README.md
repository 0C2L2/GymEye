# Gym Eye

AI-powered exercise form assistant website

Gym Eye is a smart fitness assistant prototype that helps users train with better form. The website provides camera access, real-time workout statistics, rep tracking UI, form feedback, session summaries, and dashboard history. The real AI exercise detection is designed to run separately on a Raspberry Pi or external AI device.

## What Gym Eye Does

Gym Eye is designed to:

- Detect the user during exercise
- Recognize the current exercise
- Count completed reps
- Track correct and incorrect reps
- Detect form mistakes
- Suggest corrections
- Show workout statistics
- Show session summaries
- Store or display workout history in the future

In the current version, the website uses mock/demo data for AI results. Real exercise detection will be connected later through Raspberry Pi.

## Current Features

- Landing page
- Camera page
- Browser camera access
- Start/stop camera controls
- Basic demo detection status
- Workout stats dashboard
- Rep counter UI
- Form score UI
- Mistake tracking UI
- Live feedback panel
- Session summary page
- Rep-by-rep breakdown
- Dashboard/history page with mock data
- Raspberry Pi connection status panel
- Mobile-first responsive layout

| Feature | Status |
|---|---|
| Camera preview | Working |
| Start/stop camera | Working |
| Human/face detection | Demo placeholder |
| Rep counting | Mock data |
| Form mistake detection | Mock data |
| Raspberry Pi connection | Prepared, not connected yet |
| Dashboard/history | Mock data |

## Pages

| Route | Description |
|---|---|
| `/` | Landing page explaining Gym Eye |
| `/camera` | Main camera and live workout dashboard page |
| `/session-summary` | Completed workout session summary with rep-by-rep breakdown |
| `/dashboard` | Workout history and progress dashboard using mock data |

## Raspberry Pi Integration Plan

The website does not run the main AI model. The Raspberry Pi will process camera/video or sensor input and send exercise analysis results to the website.

```txt
Camera / Sensor Input
        ↓
Raspberry Pi AI Processing
        ↓
Exercise Detection + Rep Counting + Form Analysis
        ↓
API or WebSocket Message
        ↓
Gym Eye Website Dashboard
```

The frontend is already prepared to receive structured data such as:

- person detected
- face detected
- body visibility
- current exercise
- completed reps
- correct reps
- incorrect reps
- form score
- mistakes
- correction suggestions
- confidence score
- FPS / latency

## Future AI Data Format

```json
{
  "cameraActive": true,
  "personDetected": true,
  "faceDetected": true,
  "bodyVisible": "full",
  "exercise": "squat",
  "set": 2,
  "targetReps": 15,
  "completedReps": 12,
  "correctReps": 9,
  "incorrectReps": 3,
  "formScore": 82,
  "confidence": 0.91,
  "durationSeconds": 154,
  "averageRepTimeSeconds": 3.8,
  "caloriesEstimate": 18,
  "scores": {
    "balance": 88,
    "rangeOfMotion": 76,
    "speedControl": 84,
    "posture": 79
  },
  "mistakes": [
    {
      "type": "knees_caving_inward",
      "label": "Knees caving inward",
      "severity": "medium",
      "count": 2,
      "suggestion": "Keep your knees aligned with your toes."
    }
  ],
  "activeSuggestion": "Push your knees outward.",
  "timestamp": "2026-06-03T00:00:00Z"
}
```

This payload is currently represented with mock data in the frontend. Later, the same structure can be received from Raspberry Pi through WebSocket or REST API.

## Raspberry Pi Connection Options

### Option 1: WebSocket

Best for real-time updates.

```txt
Raspberry Pi → WebSocket Server → Website
```

Use when:

- Reps update live
- Mistakes appear immediately
- Feedback changes during movement

### Option 2: REST API

Simpler for basic updates.

```txt
Website → requests latest result → Raspberry Pi API
```

Use when:

- Real-time speed is less important
- Website only refreshes stats every second or few seconds

Recommended approach: WebSocket, because Gym Eye needs live rep counting and real-time correction feedback.

## Example Raspberry Pi WebSocket Message

```js
socket.send(JSON.stringify({
  exercise: "squat",
  completedReps: 12,
  formScore: 82,
  activeSuggestion: "Keep your chest up",
  mistakes: [
    {
      label: "Back not straight",
      severity: "high",
      suggestion: "Keep your spine neutral"
    }
  ]
}));
```

The frontend can replace the current mock data with live WebSocket data later.

## Installation

```bash
npm install
```

## Running the Project

```bash
npm run dev
```

Open the website at:

```txt
http://localhost:3000
```

## Build

```bash
npm run build
```

## Lint

```bash
npm run lint
```

## Troubleshooting Next.js Chunk Errors

If the browser shows missing chunk errors such as `/_next/static/chunks/... 404` or `Cannot find module './xxx.js'`, stop the dev server and clear the Next.js cache:

```bash
rm -rf .next
npm run dev
```

Then hard refresh the browser:

- macOS Chrome: `Cmd + Shift + R`
- Windows/Linux Chrome: `Ctrl + Shift + R`

If the issue continues, reinstall dependencies:

```bash
rm -rf .next node_modules package-lock.json
npm install
npm run dev
```

## Environment Variables

The current version does not require environment variables.

In the future, Raspberry Pi connection settings may be added:

```env
NEXT_PUBLIC_AI_MODE=demo
NEXT_PUBLIC_RASPBERRY_PI_WS_URL=ws://192.168.1.50:8000/ws
NEXT_PUBLIC_RASPBERRY_PI_API_URL=http://192.168.1.50:8000
```

These values are only examples and are not required in the current demo version.

## Project Structure

```txt
src/
  app/
    page.tsx
    camera/
      page.tsx
    session-summary/
      page.tsx
    dashboard/
      page.tsx

  components/
    CameraPreview.tsx
    WorkoutStatsPanel.tsx
    RepCounter.tsx
    FeedbackPanel.tsx
    RepBreakdown.tsx
    RaspberryPiStatus.tsx
    SessionSummaryHeader.tsx
    RecentSessions.tsx

  lib/
    camera.ts
    mockDetection.ts
    mockSessions.ts
    formatters.ts

  types/
    detection.ts
    session.ts
    raspberryPi.ts
```

## Current Limitations

- Real exercise detection is not implemented yet.
- Rep counting currently uses mock data.
- Form correction currently uses mock data.
- Raspberry Pi is not connected yet.
- No database or user accounts yet.
- Workout history is currently demo data.

## Future Improvements

- Connect Raspberry Pi AI through WebSocket
- Real pose detection
- Real rep counting
- Real mistake detection
- User accounts
- Saved workout history
- Exercise library
- Voice feedback
- Trainer mode
- Mobile PWA support
- Admin/debug panel for AI model status

Gym Eye is currently a frontend prototype prepared for future AI integration. The website already provides the user interface and data structure needed for real-time exercise analysis once the Raspberry Pi AI system is connected.
