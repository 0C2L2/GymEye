import React, { useRef, useEffect, useState } from 'react';
import { PoseLandmarker, FilesetResolver, DrawingUtils } from '@mediapipe/tasks-vision';

const PI_FRAME_URL = 'http://localhost:5000/frame';

const CameraView = ({ onResults }) => {
  const canvasRef = useRef(null);
  const poseLandmarkerRef = useRef(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [modelReady, setModelReady] = useState(false);

  useEffect(() => {
    let animationFrameId;
    let drawingUtils;
    let ctx;
    let running = true;

    const setupMediaPipe = async () => {
      try {
        const vision = await FilesetResolver.forVisionTasks(
          "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@latest/wasm"
        );
        let modelOptions = {
          baseOptions: {
            modelAssetPath: `https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task`,
            delegate: "GPU"
          },
          runningMode: "IMAGE",
          numPoses: 1
        };
        try {
          poseLandmarkerRef.current = await PoseLandmarker.createFromOptions(vision, modelOptions);
        } catch {
          modelOptions.baseOptions.delegate = "CPU";
          poseLandmarkerRef.current = await PoseLandmarker.createFromOptions(vision, modelOptions);
        }

        ctx = canvasRef.current.getContext('2d');
        drawingUtils = new DrawingUtils(ctx);
        setModelReady(true);
        setLoading(false);

        const processFrame = async () => {
          if (!running) return;
          try {
            const response = await fetch(PI_FRAME_URL + '?t=' + Date.now());
            const blob = await response.blob();
            const bitmap = await createImageBitmap(blob);
            const canvas = canvasRef.current;
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.drawImage(bitmap, 0, 0, canvas.width, canvas.height);
            try {
              const results = poseLandmarkerRef.current.detect(bitmap);
              if (results.landmarks) {
                for (const landmarks of results.landmarks) {
                  drawingUtils.drawConnectors(landmarks, PoseLandmarker.POSE_CONNECTIONS);
                  drawingUtils.drawLandmarks(landmarks, {
                    radius: (data) => DrawingUtils.lerp(data.from.z, -0.15, 0.1, 5, 1)
                  });
                  onResults(landmarks);
                }
              }
            } catch (e) {}
            bitmap.close();
          } catch (e) {}
          if (running) setTimeout(processFrame, 33);
        };

        processFrame();

      } catch (err) {
        setError("Failed to load AI model.");
        setLoading(false);
      }
    };

    setupMediaPipe();

    return () => {
      running = false;
      if (poseLandmarkerRef.current) poseLandmarkerRef.current.close();
    };
  }, [onResults]);

  return (
    <div className="camera-section" style={{ position: 'relative' }}>
      {loading && <div className="loading-overlay">Loading AI Coach...</div>}
      {error && <div className="error-overlay">{error}</div>}
      <canvas
        ref={canvasRef}
        className="canvas-overlay"
        width="1280"
        height="720"
        style={{ width: '100%', height: '100%', objectFit: 'cover' }}
      />
    </div>
  );
};

export default CameraView;