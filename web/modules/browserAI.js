const MP_TASKS_URL = "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.34";

export function calculateAngle(a, b, c) {
  const radians = Math.atan2(c.y - b.y, c.x - b.x) - Math.atan2(a.y - b.y, a.x - b.x);
  let angle = Math.abs((radians * 180) / Math.PI);
  if (angle > 180) angle = 360 - angle;
  return angle;
}

class OneEuroFilter {
  constructor(freq, minCutoff = 0.5, beta = 0.007, dCutoff = 1) {
    this.freq = freq;
    this.minCutoff = minCutoff;
    this.beta = beta;
    this.dCutoff = dCutoff;
    this.xPrev = null;
    this.dxPrev = 0;
  }

  alpha(cutoff) {
    const te = 1 / this.freq;
    const tau = 1 / (2 * Math.PI * cutoff);
    return 1 / (1 + tau / te);
  }

  filter(value) {
    if (this.xPrev === null) {
      this.xPrev = value;
      return value;
    }
    const te = 1 / this.freq;
    const derivative = (value - this.xPrev) / te;
    const alphaDerivative = this.alpha(this.dCutoff);
    const dxHat = alphaDerivative * derivative + (1 - alphaDerivative) * this.dxPrev;
    const cutoff = this.minCutoff + this.beta * Math.abs(dxHat);
    const alphaValue = this.alpha(cutoff);
    const filtered = alphaValue * value + (1 - alphaValue) * this.xPrev;
    this.xPrev = filtered;
    this.dxPrev = dxHat;
    return filtered;
  }
}

class BrowserExerciseTracker {
  constructor() {
    this.exercise = "Finding Exercise...";
    this.reps = 0;
    this.correctReps = 0;
    this.incorrectReps = 0;
    this.stage = "up";
    this.startTime = performance.now();
    this.lastRepTime = null;
    this.repResults = [];
    this.mistakes = [];
    this.smoothers = new Map();
    this.history = [];
  }

  smootherFor(id) {
    if (!this.smoothers.has(id)) {
      this.smoothers.set(id, {
        x: new OneEuroFilter(30),
        y: new OneEuroFilter(30),
        z: new OneEuroFilter(30),
      });
    }
    return this.smoothers.get(id);
  }

  smoothLandmarks(landmarks) {
    return landmarks.map((landmark, index) => {
      const smoother = this.smootherFor(index);
      return {
        ...landmark,
        x: smoother.x.filter(landmark.x),
        y: smoother.y.filter(landmark.y),
        z: smoother.z.filter(landmark.z || 0),
      };
    });
  }

  detectExercise(landmarks) {
    const shoulder = landmarks[12];
    const hip = landmarks[24];
    const ankle = landmarks[28];
    const elbow = landmarks[14];
    const wrist = landmarks[16];

    const isHorizontal = Math.abs(shoulder.y - hip.y) < 0.2 && Math.abs(hip.y - ankle.y) < 0.2;
    const isVertical = Math.abs(shoulder.x - hip.x) < 0.2 && Math.abs(hip.x - ankle.x) < 0.2;

    let prediction = "Finding Exercise...";
    if (isHorizontal) {
      prediction = calculateAngle(shoulder, elbow, wrist) < 120 ? "Push-up" : "Plank";
    } else if (isVertical) {
      prediction = "Squat";
    }

    this.history.push(prediction);
    if (this.history.length > 10) this.history.shift();
    const counts = {};
    for (const item of this.history) counts[item] = (counts[item] || 0) + 1;
    const mostFrequent = Object.keys(counts).reduce((best, item) => (counts[item] > counts[best] ? item : best), prediction);

    if (mostFrequent !== this.exercise) {
      this.exercise = mostFrequent;
      this.stage = "up";
      this.reps = 0;
      this.correctReps = 0;
      this.incorrectReps = 0;
      this.repResults = [];
      this.mistakes = [];
      this.startTime = performance.now();
      this.lastRepTime = null;
    }

    return mostFrequent;
  }

  logMistake(type, label, severity, suggestion) {
    const existing = this.mistakes.find((item) => item.type === type);
    if (existing) {
      existing.count += 1;
      existing.severity = severity;
      existing.suggestion = suggestion;
      existing.label = label;
      return;
    }
    this.mistakes.push({ type, label, severity, count: 1, suggestion });
  }

  addRep(score, mistake, durationSeconds) {
    this.reps += 1;
    const correct = score >= 75;
    if (correct) this.correctReps += 1;
    else this.incorrectReps += 1;
    this.repResults.push({
      repNumber: this.reps,
      score,
      status: score >= 90 ? "excellent" : score >= 75 ? "good" : score >= 50 ? "needs_work" : "poor",
      mistake,
      durationSeconds,
      correct,
    });
  }

  update(rawLandmarks) {
    if (!rawLandmarks || rawLandmarks.length === 0) {
      return {
        cameraActive: true,
        personDetected: false,
        faceDetected: false,
        bodyVisible: "none",
        exercise: null,
        set: 1,
        targetReps: 15,
        completedReps: this.reps,
        correctReps: this.correctReps,
        incorrectReps: this.incorrectReps,
        formScore: null,
        confidence: null,
        durationSeconds: Math.round((performance.now() - this.startTime) / 1000),
        averageRepTimeSeconds: null,
        caloriesEstimate: null,
        scores: { balance: null, rangeOfMotion: null, speedControl: null, posture: null },
        angles: { leftKnee: null, rightKnee: null, leftHip: null, rightHip: null, leftElbow: null, rightElbow: null, shoulder: null, torso: null },
        mistakes: this.mistakes,
        activeSuggestion: "Stand fully inside the camera frame.",
        repResults: this.repResults,
        source: "browser_ai",
        timestamp: new Date().toISOString(),
      };
    }

    const landmarks = this.smoothLandmarks(rawLandmarks);
    const exercise = this.detectExercise(landmarks);
    const leftKnee = calculateAngle(landmarks[23], landmarks[25], landmarks[27]);
    const rightKnee = calculateAngle(landmarks[24], landmarks[26], landmarks[28]);
    const leftHip = calculateAngle(landmarks[11], landmarks[23], landmarks[25]);
    const rightHip = calculateAngle(landmarks[12], landmarks[24], landmarks[26]);
    const leftElbow = calculateAngle(landmarks[11], landmarks[13], landmarks[15]);
    const rightElbow = calculateAngle(landmarks[12], landmarks[14], landmarks[16]);

    let activeSuggestion = "No major mistake detected. Keep going.";
    let repScore = 88;
    let repMistake = null;

    if (exercise === "Squat") {
      const kneeAngle = rightKnee;
      if (kneeAngle > 165) {
        this.stage = "up";
      }
      if (kneeAngle < 95 && this.stage === "up") {
        this.stage = "down";
        const now = performance.now();
        const durationSeconds = this.lastRepTime ? (now - this.lastRepTime) / 1000 : 3.4;
        this.lastRepTime = now;

        if (leftHip < 70 || rightHip < 70) {
          repScore = 68;
          repMistake = "Not reaching full depth";
          activeSuggestion = "Lower until your hips reach at least knee level.";
          this.logMistake("not_reaching_full_depth", repMistake, "medium", activeSuggestion);
        } else if (Math.abs(leftKnee - rightKnee) > 18) {
          repScore = 72;
          repMistake = "Knees caving inward";
          activeSuggestion = "Push your knees outward and align them with your toes.";
          this.logMistake("knees_caving_inward", repMistake, "medium", activeSuggestion);
        } else {
          repScore = 91;
          activeSuggestion = "Good depth. Stay controlled on the way up.";
        }

        this.addRep(repScore, repMistake, durationSeconds);
      } else if (kneeAngle < 130 && this.stage === "up") {
        activeSuggestion = "Go slightly lower to complete the squat depth.";
      }
    } else if (exercise === "Push-up") {
      if (rightElbow > 160) this.stage = "up";
      if (rightElbow < 100 && this.stage === "up") {
        this.stage = "down";
        const now = performance.now();
        const durationSeconds = this.lastRepTime ? (now - this.lastRepTime) / 1000 : 2.6;
        this.lastRepTime = now;

        if (Math.abs(landmarks[12].y - landmarks[24].y) > 0.12) {
          repScore = 66;
          repMistake = "Back not straight";
          activeSuggestion = "Keep your spine neutral and chest proud.";
          this.logMistake("back_not_straight", repMistake, "high", activeSuggestion);
        } else {
          repScore = 89;
          activeSuggestion = "Strong push-up. Keep your core tight.";
        }

        this.addRep(repScore, repMistake, durationSeconds);
      }
    } else if (exercise === "Plank") {
      activeSuggestion = "Hold steady and keep your hips level.";
    }

    const completedReps = this.reps;
    const averageRepTimeSeconds = this.repResults.length
      ? this.repResults.reduce((sum, rep) => sum + (rep.durationSeconds || 0), 0) / this.repResults.length
      : null;
    const formScore = this.repResults.length
      ? Math.round(this.repResults.reduce((sum, rep) => sum + rep.score, 0) / this.repResults.length)
      : repScore;

    return {
      cameraActive: true,
      personDetected: true,
      faceDetected: true,
      bodyVisible: "full",
      exercise: exercise === "Finding Exercise..." ? null : exercise,
      set: 1,
      targetReps: 15,
      completedReps,
      correctReps: this.correctReps,
      incorrectReps: this.incorrectReps,
      formScore,
      confidence: exercise === "Finding Exercise..." ? 0.4 : 0.88,
      durationSeconds: Math.round((performance.now() - this.startTime) / 1000),
      averageRepTimeSeconds,
      caloriesEstimate: completedReps > 0 ? Math.round(completedReps * 1.2) : null,
      scores: {
        balance: Math.round(100 - Math.min(20, Math.abs(leftKnee - rightKnee))),
        rangeOfMotion: Math.round(Math.max(55, 100 - Math.abs(90 - rightKnee))),
        speedControl: averageRepTimeSeconds ? Math.round(Math.min(95, 65 + averageRepTimeSeconds * 8)) : 80,
        posture: repMistake === "Back not straight" ? 62 : 84,
      },
      angles: {
        leftKnee,
        rightKnee,
        leftHip,
        rightHip,
        leftElbow,
        rightElbow,
        shoulder: calculateAngle(landmarks[11], landmarks[12], landmarks[24]),
        torso: calculateAngle(landmarks[12], landmarks[24], landmarks[28]),
      },
      mistakes: this.mistakes,
      activeSuggestion,
      repResults: this.repResults,
      source: "browser_ai",
      timestamp: new Date().toISOString(),
      poseLandmarks: rawLandmarks.map((item) => [item.x, item.y, item.z || 0]),
    };
  }
}

export class BrowserPoseController {
  constructor({ videoEl, canvasEl, onAnalysis }) {
    this.videoEl = videoEl;
    this.canvasEl = canvasEl;
    this.onAnalysis = onAnalysis;
    this.landmarker = null;
    this.stream = null;
    this.running = false;
    this.animationId = null;
    this.tracker = new BrowserExerciseTracker();
    this.drawingUtils = null;
  }

  async start() {
    if (this.running) return;
    this.stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
    this.videoEl.srcObject = this.stream;
    await this.videoEl.play();

    const { PoseLandmarker, FilesetResolver, DrawingUtils } = await import(MP_TASKS_URL);
    const vision = await FilesetResolver.forVisionTasks(`${MP_TASKS_URL}/wasm`);
    this.landmarker = await PoseLandmarker.createFromOptions(vision, {
      baseOptions: {
        modelAssetPath:
          "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task",
        delegate: "GPU",
      },
      runningMode: "VIDEO",
      numPoses: 1,
    });

    const context = this.canvasEl.getContext("2d");
    this.drawingUtils = new DrawingUtils(context);
    this.running = true;
    this.loop();
  }

  loop() {
    if (!this.running) return;
    const width = this.videoEl.videoWidth || 1280;
    const height = this.videoEl.videoHeight || 720;
    this.canvasEl.width = width;
    this.canvasEl.height = height;

    const context = this.canvasEl.getContext("2d");
    context.clearRect(0, 0, width, height);

    const results = this.landmarker.detectForVideo(this.videoEl, performance.now());
    const landmarks = results.landmarks?.[0] || null;

    if (landmarks) {
      this.drawingUtils.drawConnectors(landmarks, this.landmarker.constructor.POSE_CONNECTIONS);
      this.drawingUtils.drawLandmarks(landmarks, { radius: 3 });
    }

    const analysis = this.tracker.update(landmarks);
    this.onAnalysis(analysis);
    this.animationId = window.requestAnimationFrame(() => this.loop());
  }

  stop() {
    this.running = false;
    if (this.animationId) cancelAnimationFrame(this.animationId);
    if (this.landmarker?.close) this.landmarker.close();
    if (this.stream) {
      this.stream.getTracks().forEach((track) => track.stop());
    }
    this.videoEl.srcObject = null;
    const context = this.canvasEl.getContext("2d");
    context.clearRect(0, 0, this.canvasEl.width, this.canvasEl.height);
  }
}
