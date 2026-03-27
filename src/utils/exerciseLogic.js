/**
 * Calculates the angle between three points (A, B, C) where B is the vertex.
 */
export const calculateAngle = (a, b, c) => {
  const radians = Math.atan2(c.y - b.y, c.x - b.x) - Math.atan2(a.y - b.y, a.x - b.x);
  let angle = Math.abs((radians * 180.0) / Math.PI);
  if (angle > 180.0) {
    angle = 360 - angle;
  }
  return angle;
};

export const EXERCISES = {
  SQUAT: 'Squat',
  PUSHUP: 'Push-up',
  PLANK: 'Plank',
  NONE: 'Finding Exercise...',
};

/**
 * One Euro Filter for smoothing jittery real-time data.
 */
class OneEuroFilter {
  constructor(freq, mincutoff = 1.0, beta = 0.0, dcutoff = 1.0) {
    this.freq = freq;
    this.mincutoff = mincutoff;
    this.beta = beta;
    this.dcutoff = dcutoff;
    this.xPrev = null;
    this.dxPrev = null;
  }

  alpha(cutoff) {
    const te = 1.0 / this.freq;
    const tau = 1.0 / (2 * Math.PI * cutoff);
    return 1.0 / (1.0 + tau / te);
  }

  filter(x) {
    if (this.xPrev === null) {
      this.xPrev = x;
      this.dxPrev = 0;
      return x;
    }

    const te = 1.0 / this.freq;
    const adx = this.alpha(this.dcutoff);
    const dx = (x - this.xPrev) / te;
    const dxHat = adx * dx + (1.0 - adx) * this.dxPrev;

    const cutoff = this.mincutoff + this.beta * Math.abs(dxHat);
    const ax = this.alpha(cutoff);
    const xHat = ax * x + (1.0 - ax) * this.xPrev;

    this.xPrev = xHat;
    this.dxPrev = dxHat;
    return xHat;
  }
}

export class ExerciseTracker {
  constructor() {
    this.count = 0;
    this.stage = 'up';
    this.feedback = '';
    this.detectedExercise = EXERCISES.NONE;
    
    // Smoothers for important landmarks (Hips, Knees, Shoulders, Elbows)
    this.smoothers = {};
    this.history = []; // Hold recent exercise predictions for stability
  }

  getSmoother(id) {
    if (!this.smoothers[id]) {
        // x, y, z filters
      this.smoothers[id] = {
        x: new OneEuroFilter(30, 0.5, 0.007),
        y: new OneEuroFilter(30, 0.5, 0.007),
        z: new OneEuroFilter(30, 0.5, 0.007)
      };
    }
    return this.smoothers[id];
  }

  smoothLandmarks(landmarks) {
    return landmarks.map((lm, i) => {
      const s = this.getSmoother(i);
      return {
        ...lm,
        x: s.x.filter(lm.x),
        y: s.y.filter(lm.y),
        z: s.z.filter(lm.z)
      };
    });
  }

  detectExercise(landmarks) {
    // MediaPipe Landmarks: 12 (R-Shoulder), 24 (R-Hip), 28 (R-Ankle)
    const shoulder = landmarks[12];
    const hip = landmarks[24];
    const ankle = landmarks[28];
    const elbow = landmarks[14];

    // Check orientation
    const isHorizontal = Math.abs(shoulder.y - hip.y) < 0.2 && Math.abs(hip.y - ankle.y) < 0.2;
    const isVertical = Math.abs(shoulder.x - hip.x) < 0.2 && Math.abs(hip.x - ankle.x) < 0.2;

    let prediction = EXERCISES.NONE;

    if (isHorizontal) {
       // Check elbow angle to distinguish between Plank and Push-up
       const elbowAngle = calculateAngle(shoulder, elbow, landmarks[16]);
       if (elbowAngle < 120) {
          prediction = EXERCISES.PUSHUP;
       } else {
          prediction = EXERCISES.PLANK;
       }
    } else if (isVertical) {
       prediction = EXERCISES.SQUAT;
    }

    // Stabilize prediction over 10 frames
    this.history.push(prediction);
    if (this.history.length > 10) this.history.shift();
    
    const counts = {};
    this.history.forEach(ex => counts[ex] = (counts[ex] || 0) + 1);
    const mostFreq = Object.keys(counts).reduce((a, b) => counts[a] > counts[b] ? a : b);

    if (mostFreq !== this.detectedExercise) {
        this.detectedExercise = mostFreq;
        this.reset();
    }
    return mostFreq;
  }

  update(rawLandmarks) {
    if (!rawLandmarks || rawLandmarks.length === 0) return { count: this.count, feedback: 'Position yourself in frame', exercise: this.detectedExercise };

    const landmarks = this.smoothLandmarks(rawLandmarks);
    const exercise = this.detectExercise(landmarks);

    switch (exercise) {
      case EXERCISES.SQUAT:
        return { ...this.processSquat(landmarks), exercise };
      case EXERCISES.PUSHUP:
        return { ...this.processPushUp(landmarks), exercise };
      default:
        return { count: this.count, feedback: '', exercise, angle: 180 };
    }
  }

  processSquat(landmarks) {
    const hip = landmarks[24];
    const knee = landmarks[26];
    const ankle = landmarks[28];
    const angle = calculateAngle(hip, knee, ankle);

    if (angle > 165) {
      this.stage = 'up';
      this.feedback = '';
    }
    if (angle < 95 && this.stage === 'up') {
      this.stage = 'down';
      this.count++;
      this.feedback = 'Good Depth!';
    } else if (angle < 130 && angle > 95 && this.stage === 'up') {
        this.feedback = 'Go Lower!';
    }

    return { count: this.count, feedback: this.feedback, angle };
  }

  processPushUp(landmarks) {
    const shoulder = landmarks[12];
    const elbow = landmarks[14];
    const wrist = landmarks[16];
    const angle = calculateAngle(shoulder, elbow, wrist);

    if (angle > 160) {
      this.stage = 'up';
      this.feedback = '';
    }
    if (angle < 100 && this.stage === 'up') {
      this.stage = 'down';
      this.count++;
      this.feedback = 'Great Push-up!';
    }

    return { count: this.count, feedback: this.feedback, angle };
  }

  reset() {
    this.count = 0;
    this.stage = 'up';
    this.feedback = '';
  }
}
