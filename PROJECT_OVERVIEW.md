# AI Gym Coach - Project Overview

## 💡 Core Concept
The AI Gym Coach is a computer vision-based fitness application that turns any smartphone or laptop camera into a personal trainer. It uses on-device machine learning to track body posture, count repetitions, and provide real-time feedback without the need for wearable hardware.

## 🚀 Implementation Status: **Phase 5 (Completed)**
The project has evolved from a basic pose-tracking prototype into a fully autonomous coaching system with history persistence.

### 📅 Accomplishments So Far:
1.  **Phase 1: Foundation (DONE)**
    *   Vite + React framework setup.
    *   Premium dark-themed design system (Glassmorphism).
2.  **Phase 2: AI Integration (DONE)**
    *   MediaPipe **BlazePose** integration for 33-point skeletal tracking.
    *   High-performance GPU-accelerated inferencing in the browser.
3.  **Phase 3: Exercise Intelligence (DONE)**
    *   Initial logic for **Squats**, **Push-ups**, and **Planks**.
    *   Angle-based state machines for reliable rep counting.
4.  **Phase 4: Refinement & Smoothing (DONE)**
    *   Implemented **One-Euro Filter** to eliminate jitter in skeletal tracking.
    *   Added **Automatic Exercise Detection** (Pose-based classifier).
5.  **Phase 5: Data Persistence & Badges (DONE)**
    *   `localStorage` integration for persistent workout history.
    *   Real-time **Badge Collection** system within sessions.
    *   Sliding menu sidebar for reviewing past performance.

---

## 🛠️ Current Tech Stack
- **Frontend**: React 18, Vite.
- **AI/CV**: MediaPipe Tasks Vision.
- **Styling**: Vanilla CSS (Custom properties & Glassmorphism).
- **Icons**: Lucide React.
- **Storage**: Browser LocalStorage.

## 🎯 Next Steps (Proposed)
- [ ] **Mobile App Port**: Transitioning to React Native or PWA optimization for smartphone use.
- [ ] **Audio Coaching**: Voice feedback for eyes-free training.
- [ ] **Advanced Analytics**: Weekly progress charts and muscle fatigue estimates.
