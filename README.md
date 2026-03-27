# AI Gym Coach 🏋️‍♂️🤖

> **Transform any smartphone or laptop camera into a personal AI fitness coach.**

[![Vite](https://img.shields.io/badge/Vite-B73BFE?style=for-the-badge&logo=vite&logoColor=FFD62E)](https://vitejs.dev/)
[![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://reactjs.org/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-00D1FF?style=for-the-badge&logo=google&logoColor=white)](https://mediapipe.dev/)

---

## 🌟 Overview
**AI Gym Coach** is a real-time computer vision application that provides professional-grade fitness guidance using only your browser. By leveraging on-device machine learning, it tracks your body mechanics, counts your repetitions, and gives you instant feedback on your form—ensuring every rep counts while minimizing injury risk.

---

## 🔥 Key Features

### 🔍 Automatic Exercise Detection
No more manual selecting! The AI intelligently identifies whether you're performing **Squats**, **Push-ups**, or **Planks** based on your body orientation and joint angles.

### 🛡️ One-Euro Smoothing
Integrated jitter-reduction logic ensure that the skeletal overlay and angle tracking remain stable even in variable lighting conditions, providing a premium, jitter-free experience.

### 🏆 Session Badges & History
Stay motivated by "collecting" workout badges during your session. Once finished, save your performance to the **History Sidebar** to track your progress over days and weeks.

### 💎 Premium Dark UI
A futuristic, glassmorphic interface designed for clarity and visual impact. Real-time stats cards keep you focused on your goals.

---

## 🛠️ Tech Stack
- **Frontend Core**: React 18 & Vite
- **Computer Vision**: Google MediaPipe (BlazePose)
- **Styling**: Vanilla CSS (Modern Custom Properties)
- **State Management**: React Hooks & LocalStorage
- **Icons**: Lucide React

---

## 🚀 Getting Started

### Prerequisites
- [Node.js](https://nodejs.org/) (v18 or higher recommended)
- A webcam-enabled device

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/ai-gym-coach.git
   cd ai-gym-coach
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```
4. Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## 🧭 Usage
1. Position your device so your full body is visible in the frame.
2. Begin moving! The AI will detect the exercise and start tracking your reps.
3. Use the **Save & Reset** button to store your session data.
4. Access the **Menu icon** (top right) to review your workout history.

---

## 📜 License
Distributed under the MIT License. See `LICENSE` for more information.

---
*Developed with ❤️ by Antigravity*
