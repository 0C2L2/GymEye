import cv2
import numpy as np
import requests
import threading
import time
from flask import Flask, Response
import urllib.request
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.tasks.python.vision import PoseLandmarkerOptions
from mediapipe.tasks.python.vision.core.vision_task_running_mode import VisionTaskRunningMode
import mediapipe as mp
import urllib.request as ur

PI_URL = "http://gymEye-cam.local:5000"
PI_SERVO_URL = "http://gymEye-cam.local:5000/servo"

app = Flask(__name__)

# Download model if not exists
import os
MODEL_PATH = "pose_landmarker_lite.task"
if not os.path.exists(MODEL_PATH):
    print("Downloading pose model...")
    ur.urlretrieve(
        "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task",
        MODEL_PATH
    )
    print("Model downloaded!")

# Setup PoseLandmarker
base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
options = PoseLandmarkerOptions(
    base_options=base_options,
    running_mode=VisionTaskRunningMode.IMAGE,
    num_poses=1
)
landmarker = vision.PoseLandmarker.create_from_options(options)

latest_frame = None
frame_lock = threading.Lock()
state = {
    'exercise': 'Finding Exercise...',
    'reps': 0,
    'feedback': 'Stand in front of camera',
    'angle': 180,
    'stage': 'up'
}

def calculate_angle(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    if angle > 180.0:
        angle = 360 - angle
    return angle

def get_point(landmarks, idx, w, h):
    lm = landmarks[idx]
    return [lm.x * w, lm.y * h]

def detect_exercise(landmarks):
    shoulder = landmarks[12]
    hip = landmarks[24]
    ankle = landmarks[28]
    elbow = landmarks[14]
    is_horizontal = abs(shoulder.y - hip.y) < 0.2 and abs(hip.y - ankle.y) < 0.2
    is_vertical = abs(shoulder.x - hip.x) < 0.2 and abs(hip.x - ankle.x) < 0.2
    if is_horizontal:
        return 'Push-up'
    elif is_vertical:
        return 'Squat'
    return 'Finding Exercise...'

def process_squat(landmarks, h, w):
    hip = get_point(landmarks, 24, w, h)
    knee = get_point(landmarks, 26, w, h)
    ankle = get_point(landmarks, 28, w, h)
    angle = calculate_angle(hip, knee, ankle)
    if angle > 165:
        state['stage'] = 'up'
    if angle < 95 and state['stage'] == 'up':
        state['stage'] = 'down'
        state['reps'] += 1
        state['feedback'] = 'Good Depth! Rep counted!'
    elif angle < 130 and state['stage'] == 'up':
        state['feedback'] = 'Go Lower!'
    elif angle > 165:
        state['feedback'] = 'Ready!'
    state['angle'] = round(angle)

def process_pushup(landmarks, h, w):
    shoulder = get_point(landmarks, 12, w, h)
    elbow = get_point(landmarks, 14, w, h)
    wrist = get_point(landmarks, 16, w, h)
    angle = calculate_angle(shoulder, elbow, wrist)
    if angle > 160:
        state['stage'] = 'up'
    if angle < 100 and state['stage'] == 'up':
        state['stage'] = 'down'
        state['reps'] += 1
        state['feedback'] = 'Great Push-up!'
    elif angle > 100 and angle < 160 and state['stage'] == 'up':
        state['feedback'] = 'Lower more!'
    state['angle'] = round(angle)

last_servo_time = 0

def send_servo(pan, tilt):
    global last_servo_time
    now = time.time()
    if now - last_servo_time < 0.5:
        return
    last_servo_time = now
    try:
        requests.get(f"{PI_SERVO_URL}?pan={pan}&tilt={tilt}", timeout=0.3)
    except:
        pass

def track_servos(landmarks):
    ls, rs = landmarks[11], landmarks[12]
    lh, rh = landmarks[23], landmarks[24]
    cx = (ls.x + rs.x + lh.x + rh.x) / 4
    cy = (ls.y + rs.y + lh.y + rh.y) / 4
    pan = 'stop'
    tilt = 90
    centered = True
    if cx < 0.35:
        pan = 'left'
        centered = False
    elif cx > 0.65:
        pan = 'right'
        centered = False
    if cy < 0.3:
        tilt = 60
        centered = False
    elif cy > 0.7:
        tilt = 120
        centered = False
    send_servo(pan, tilt)
    return centered

def draw_landmarks_manual(frame, landmarks, w, h):
    connections = [
        (11,12),(11,13),(13,15),(12,14),(14,16),
        (11,23),(12,24),(23,24),(23,25),(24,26),
        (25,27),(26,28),(27,29),(28,30),(29,31),(30,32)
    ]
    for a, b in connections:
        ax, ay = int(landmarks[a].x*w), int(landmarks[a].y*h)
        bx, by = int(landmarks[b].x*w), int(landmarks[b].y*h)
        cv2.line(frame, (ax,ay), (bx,by), (0,209,255), 2)
    for lm in landmarks:
        cx, cy = int(lm.x*w), int(lm.y*h)
        cv2.circle(frame, (cx,cy), 4, (0,209,255), -1)

def capture_and_process():
    global latest_frame
    stream = urllib.request.urlopen(f"{PI_URL}/stream")
    buf = b''
    while True:
        buf += stream.read(4096)
        start = buf.find(b'\xff\xd8')
        end = buf.find(b'\xff\xd9')
        if start != -1 and end != -1 and end > start:
            jpg = buf[start:end+2]
            buf = buf[end+2:]
            frame = cv2.imdecode(np.frombuffer(jpg, np.uint8), cv2.IMREAD_COLOR)
            if frame is None:
                continue
            h, w = frame.shape[:2]
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB,
                               data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            result = landmarker.detect(mp_image)
            if result.pose_landmarks and len(result.pose_landmarks) > 0:
                landmarks = result.pose_landmarks[0]
                centered = track_servos(landmarks)
                draw_landmarks_manual(frame, landmarks, w, h)
                if centered:
                    exercise = detect_exercise(landmarks)
                    if exercise != state['exercise']:
                        state['exercise'] = exercise
                        state['reps'] = 0
                        state['stage'] = 'up'
                    if exercise == 'Squat':
                        process_squat(landmarks, h, w)
                    elif exercise == 'Push-up':
                        process_pushup(landmarks, h, w)
                else:
                    state['feedback'] = 'Move to center!'

                cv2.putText(frame, f"{state['exercise']}", (10,40),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0,209,255), 2)
                cv2.putText(frame, f"Reps: {state['reps']}", (10,80),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0,209,255), 2)
                cv2.putText(frame, f"Angle: {state['angle']}", (10,120),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (157,80,187), 2)
                cv2.putText(frame, state['feedback'], (10,160),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,136), 2)

            _, jpeg = cv2.imencode('.jpg', frame)
            with frame_lock:
                latest_frame = jpeg.tobytes()

def generate():
    while True:
        with frame_lock:
            frame = latest_frame
        if frame:
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        time.sleep(0.033)

HTML = '''<!DOCTYPE html>
<html>
<head><title>GymEye AI Coach</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{background:#0F0F12;color:white;font-family:Arial;display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:100vh;}
h1{color:#00D1FF;margin-bottom:15px;}
img{width:800px;height:600px;border-radius:16px;box-shadow:0 0 30px rgba(0,209,255,0.3);}
</style>
</head>
<body>
<h1>GymEye AI Coach</h1>
<img src="/stream"/>
</body>
</html>'''

@app.route('/')
def index():
    return HTML

@app.route('/stream')
def stream_route():
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    print("Starting GymEye Server...")
    t = threading.Thread(target=capture_and_process, daemon=True)
    t.start()
    time.sleep(3)
    print("Open browser at http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)