import React, { useRef, useEffect, useState } from 'react';
import { PoseLandmarker, FilesetResolver, DrawingUtils } from '@mediapipe/tasks-vision';

const CameraView = ({ onResults }) => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let poseLandmarker;
    let animationFrameId;
    let drawingUtils;
    let ctx;

    const setupMediaPipe = async () => {
      try {
        const vision = await FilesetResolver.forVisionTasks(
          "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@latest/wasm"
        );
        poseLandmarker = await PoseLandmarker.createFromOptions(vision, {
          baseOptions: {
            modelAssetPath: `https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task`,
            delegate: "GPU"
          },
          runningMode: "VIDEO",
          numPoses: 1
        });
        
        ctx = canvasRef.current.getContext('2d');
        drawingUtils = new DrawingUtils(ctx);
        setLoading(false);
        startCamera();
      } catch (err) {
        console.error("MediaPipe Init Error:", err);
        setError("Failed to load AI model. Please check your connection.");
        setLoading(false);
      }
    };

    const startCamera = async () => {
      if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        try {
          const stream = await navigator.mediaDevices.getUserMedia({
            video: { width: 1280, height: 720 },
            audio: false
          });
          videoRef.current.srcObject = stream;
          videoRef.current.onloadedmetadata = () => {
            videoRef.current.play();
            requestAnimationFrame(predictWebcam);
          };
        } catch (err) {
          console.error("Camera Error:", err);
          setError("Camera access denied. Please allow camera permissions.");
        }
      }
    };

    let lastVideoTime = -1;
    const predictWebcam = () => {
      if (videoRef.current && videoRef.current.readyState >= 2) {
        let startTimeMs = performance.now();
        if (lastVideoTime !== videoRef.current.currentTime) {
          lastVideoTime = videoRef.current.currentTime;
          const results = poseLandmarker.detectForVideo(videoRef.current, startTimeMs);

          // Clear canvas
          ctx.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height);

          if (results.landmarks) {
            for (const landmarks of results.landmarks) {
              drawingUtils.drawConnectors(landmarks, PoseLandmarker.POSE_CONNECTIONS);
              drawingUtils.drawLandmarks(landmarks, { radius: (data) => DrawingUtils.lerp(data.from.z, -0.15, 0.1, 5, 1) });
              onResults(landmarks);
            }
          }
        }
      }
      animationFrameId = requestAnimationFrame(predictWebcam);
    };

    setupMediaPipe();

    return () => {
      if (animationFrameId) cancelAnimationFrame(animationFrameId);
      if (poseLandmarker) poseLandmarker.close();
      if (videoRef.current && videoRef.current.srcObject) {
          videoRef.current.srcObject.getTracks().forEach(track => track.stop());
      }
    };
  }, [onResults]);

  return (
    <div className="camera-section">
      {loading && <div className="loading-overlay">Loading AI Coach...</div>}
      {error && <div className="error-overlay">{error}</div>}
      <video
        ref={videoRef}
        className="video-feed"
        autoPlay
        playsInline
      />
      <canvas
        ref={canvasRef}
        className="canvas-overlay"
        width="1280"
        height="720"
      />
    </div>
  );
};

export default CameraView;
