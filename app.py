from http.server import BaseHTTPRequestHandler, HTTPServer
import subprocess, threading, time
from urllib.parse import urlparse, parse_qs

# Arduino serial connection
try:
    import serial
    arduino = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
    time.sleep(2)
    print("Arduino connected!")
except Exception as e:
    arduino = None
    print(f"Arduino not found: {e}")

latest_frame = b''
lock = threading.Lock()
last_servo_time = 0

def send_servo(pan_dir, tilt_angle):
    global last_servo_time
    if arduino is None:
        return
    now = time.time()
    if now - last_servo_time < 0.5:
        return
    last_servo_time = now
    if pan_dir == 'left':
        arduino.write(b'PAN:LEFT\n')
    elif pan_dir == 'right':
        arduino.write(b'PAN:RIGHT\n')
    if tilt_angle is not None:
        cmd = f'TILT:{tilt_angle}\n'.encode()
        arduino.write(cmd)

def capture():
    global latest_frame
    proc = subprocess.Popen(
          ['ffmpeg', '-f', 'v4l2', '-framerate', '30',
          '-video_size', '640x480', '-i', '/dev/video0',
          '-vcodec', 'mjpeg', '-q:v', '3',
          '-f', 'image2pipe', 'pipe:1'],
          stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=0)
    buf = b''
    while True:
        buf += proc.stdout.read(4096)
        s, e = buf.find(b'\xff\xd8'), buf.find(b'\xff\xd9')
        if s != -1 and e != -1 and e > s:
            with lock:
                latest_frame = buf[s:e+2]
            buf = buf[e+2:]

threading.Thread(target=capture, daemon=True).start()
time.sleep(3)

HTML = b'''<!DOCTYPE html>
<html>
<head>
<title>GymEye AI Coach</title>
<style>
*{box-sizing:border-box;margin:0;padding:0;}
body{background:#0F0F12;font-family:Arial;color:white;overflow:hidden;}
#container{position:fixed;top:0;left:0;width:100vw;height:100vh;}
#stream{position:absolute;top:0;left:0;width:100%;height:100%;object-fit:cover;}
canvas{position:absolute;top:0;left:0;width:100%;height:100%;}
.overlay-stats{position:fixed;bottom:0;left:0;right:0;display:flex;gap:15px;padding:20px;background:linear-gradient(transparent,rgba(0,0,0,0.85));justify-content:center;align-items:flex-end;flex-wrap:wrap;}
.card{background:rgba(0,0,0,0.6);border:2px solid rgba(255,255,255,0.15);border-radius:16px;padding:15px 25px;text-align:center;min-width:140px;backdrop-filter:blur(10px);}
.card-label{color:#A0A0A0;font-size:14px;text-transform:uppercase;margin-bottom:6px;}
.card-value{font-size:42px;font-weight:bold;color:#00D1FF;}
#feedback-card{min-width:400px;border-color:rgba(255,68,68,0.4);}
#feedback-val{color:#FF6666;font-size:22px;font-weight:bold;line-height:1.4;}
.good{color:#00FF88!important;}
.header{position:fixed;top:0;left:0;right:0;display:flex;justify-content:space-between;align-items:center;padding:15px 25px;background:linear-gradient(rgba(0,0,0,0.7),transparent);}
.title{color:#00D1FF;font-size:26px;font-weight:bold;}
#status{color:#00D1FF;font-size:16px;}
#legend{display:flex;gap:15px;font-size:13px;color:#ccc;}
.legend-item{display:flex;align-items:center;gap:6px;}
.dot{width:14px;height:14px;border-radius:50%;}
</style>
</head>
<body>
<div class="header">
  <div class="title">GymEye AI Coach</div>
  <div id="legend">
    <div class="legend-item"><div class="dot" style="background:#00D1FF"></div>Your pose</div>
    <div class="legend-item"><div class="dot" style="background:#00FF88"></div>Good joint</div>
    <div class="legend-item"><div class="dot" style="background:#FF4444"></div>Needs fix</div>
  </div>
  <div id="status">Loading AI...</div>
</div>

<div id="container">
  <img id="stream" src="/stream" crossorigin="anonymous"/>
  <canvas id="canvas"></canvas>
</div>

<div class="overlay-stats">
  <div class="card">
    <div class="card-label">Exercise</div>
    <div class="card-value" id="exercise-val" style="font-size:22px;color:#9D50BB;">Detecting...</div>
  </div>
  <div class="card">
    <div class="card-label">Reps</div>
    <div class="card-value" id="reps-val">0</div>
  </div>
  <div class="card">
    <div class="card-label">Angle</div>
    <div class="card-value" id="angle-val">0</div>
  </div>
  <div class="card" id="feedback-card">
    <div class="card-label">Coach Feedback</div>
    <div class="card-value" id="feedback-val">Stand in front of camera</div>
  </div>
</div>

<script type="module">
import { PoseLandmarker, FilesetResolver, DrawingUtils } from "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision/vision_bundle.mjs";

const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");
const img = document.getElementById("stream");
const statusEl = document.getElementById("status");
const repsEl = document.getElementById("reps-val");
const angleEl = document.getElementById("angle-val");
const exerciseEl = document.getElementById("exercise-val");
const feedbackEl = document.getElementById("feedback-val");

function resizeCanvas(){canvas.width=window.innerWidth;canvas.height=window.innerHeight;}
resizeCanvas();
window.addEventListener("resize",resizeCanvas);

const IDEAL = {
  Squat:{
    knee:{ideal:90,tolerance:15,landmarks:[24,26,28]},
    hip:{ideal:90,tolerance:15,landmarks:[12,24,26]},
    back:{ideal:180,tolerance:20,landmarks:[12,24,28]}
  },
  "Push-up":{
    elbow:{ideal:90,tolerance:15,landmarks:[12,14,16]},
    shoulder:{ideal:45,tolerance:15,landmarks:[14,12,24]},
    back:{ideal:180,tolerance:20,landmarks:[12,24,28]}
  },
  Plank:{
    hip:{ideal:180,tolerance:15,landmarks:[12,24,28]},
    elbow:{ideal:90,tolerance:15,landmarks:[12,14,16]}
  }
};

class OneEuroFilter {
  constructor(freq,mincutoff=1.0,beta=0.0,dcutoff=1.0){this.freq=freq;this.mincutoff=mincutoff;this.beta=beta;this.dcutoff=dcutoff;this.xPrev=null;this.dxPrev=null;}
  alpha(cutoff){const te=1/this.freq,tau=1/(2*Math.PI*cutoff);return 1/(1+tau/te);}
  filter(x){if(this.xPrev===null){this.xPrev=x;this.dxPrev=0;return x;}const adx=this.alpha(this.dcutoff),dx=(x-this.xPrev)*this.freq;const dxHat=adx*dx+(1-adx)*this.dxPrev;const cutoff=this.mincutoff+this.beta*Math.abs(dxHat);const ax=this.alpha(cutoff),xHat=ax*x+(1-ax)*this.xPrev;this.xPrev=xHat;this.dxPrev=dxHat;return xHat;}
}

class ExerciseTracker {
  constructor(){this.count=0;this.stage="up";this.feedback="";this.detectedExercise="Finding Exercise...";this.smoothers={};this.history=[];}
  getSmoother(id){if(!this.smoothers[id])this.smoothers[id]={x:new OneEuroFilter(30,0.5,0.007),y:new OneEuroFilter(30,0.5,0.007),z:new OneEuroFilter(30,0.5,0.007)};return this.smoothers[id];}
  smoothLandmarks(lms){return lms.map((lm,i)=>{const s=this.getSmoother(i);return{...lm,x:s.x.filter(lm.x),y:s.y.filter(lm.y),z:s.z.filter(lm.z)};});}
  calcAngle(a,b,c){const r=Math.atan2(c.y-b.y,c.x-b.x)-Math.atan2(a.y-b.y,a.x-b.x);let ang=Math.abs(r*180/Math.PI);if(ang>180)ang=360-ang;return ang;}
  detectExercise(lms){
    const shoulder=lms[12],hip=lms[24],ankle=lms[28],elbow=lms[14];
    const isHorizontal=Math.abs(shoulder.y-hip.y)<0.2&&Math.abs(hip.y-ankle.y)<0.2;
    const isVertical=Math.abs(shoulder.x-hip.x)<0.2&&Math.abs(hip.x-ankle.x)<0.2;
    let pred="Finding Exercise...";
    if(isHorizontal){const ea=this.calcAngle(shoulder,elbow,lms[16]);pred=ea<120?"Push-up":"Plank";}
    else if(isVertical)pred="Squat";
    this.history.push(pred);if(this.history.length>10)this.history.shift();
    const counts={};this.history.forEach(ex=>counts[ex]=(counts[ex]||0)+1);
    const mostFreq=Object.keys(counts).reduce((a,b)=>counts[a]>counts[b]?a:b);
    if(mostFreq!==this.detectedExercise){this.detectedExercise=mostFreq;this.reset();}
    return mostFreq;
  }
  getJointStatus(lms,exercise){
    const status={};const ideal=IDEAL[exercise];if(!ideal)return status;
    for(const[key,conf]of Object.entries(ideal)){
      const[ai,bi,ci]=conf.landmarks;
      const ang=this.calcAngle(lms[ai],lms[bi],lms[ci]);
      status[key]={angle:ang,good:Math.abs(ang-conf.ideal)<=conf.tolerance,ideal:conf.ideal,pos:lms[bi]};
    }
    return status;
  }
  update(rawLms){
    if(!rawLms||rawLms.length===0)return{count:this.count,feedback:"Get in frame",exercise:this.detectedExercise,angle:180,jointStatus:{}};
    const lms=this.smoothLandmarks(rawLms);
    const exercise=this.detectExercise(lms);
    if(exercise==="Squat")return{...this.processSquat(lms),exercise};
    if(exercise==="Push-up")return{...this.processPushUp(lms),exercise};
    if(exercise==="Plank")return{...this.processPlank(lms),exercise};
    return{count:this.count,feedback:"",exercise,angle:180,jointStatus:{}};
  }
  processSquat(lms){
    const a=this.calcAngle(lms[24],lms[26],lms[28]);
    const jointStatus=this.getJointStatus(lms,"Squat");
    const feedbacks=[];
    if(!jointStatus.back?.good)feedbacks.push("Keep your back straight!");
    if(a>165){this.stage="up";}
    if(a<95&&this.stage==="up"){this.stage="down";this.count++;feedbacks.unshift("Good Depth! Rep counted!");}
    else if(a<130&&a>95&&this.stage==="up")feedbacks.unshift("Go Lower! Bend knees more");
    else if(a>165)feedbacks.unshift("Ready - start squatting!");
    this.feedback=feedbacks[0]||"Good form! Keep going!";
    return{count:this.count,feedback:this.feedback,angle:Math.round(a),jointStatus};
  }
  processPushUp(lms){
    const a=this.calcAngle(lms[12],lms[14],lms[16]);
    const jointStatus=this.getJointStatus(lms,"Push-up");
    const feedbacks=[];
    if(!jointStatus.back?.good)feedbacks.push("Keep core tight - no sagging!");
    if(a>160){this.stage="up";}
    if(a<100&&this.stage==="up"){this.stage="down";this.count++;feedbacks.unshift("Great Push-up! Rep counted!");}
    else if(a>100&&a<160&&this.stage==="up")feedbacks.unshift("Lower your chest more!");
    this.feedback=feedbacks[0]||"Good form!";
    return{count:this.count,feedback:this.feedback,angle:Math.round(a),jointStatus};
  }
  processPlank(lms){
    const jointStatus=this.getJointStatus(lms,"Plank");
    const feedbacks=[];
    if(!jointStatus.hip?.good){if(jointStatus.hip?.angle<170)feedbacks.push("Raise your hips - stay straight!");else feedbacks.push("Lower hips - no pike!");}
    if(!jointStatus.elbow?.good)feedbacks.push("Keep elbows at 90 degrees!");
    this.feedback=feedbacks[0]||"Perfect Plank! Hold it!";
    return{count:this.count,feedback:this.feedback,angle:Math.round(jointStatus.hip?.angle||180),jointStatus};
  }
  reset(){this.count=0;this.stage="up";this.feedback="";}
}

const tracker=new ExerciseTracker();
let poseLandmarker,drawingUtils;

function drawIdealPose(lms,exercise,jointStatus){
  if(!IDEAL[exercise])return;
  const W=canvas.width,H=canvas.height;
  for(const[key,status]of Object.entries(jointStatus)){
    const x=status.pos.x*W;
    const y=status.pos.y*H;
    const color=status.good?"#00FF88":"#FF4444";
    ctx.beginPath();ctx.arc(x,y,16,0,2*Math.PI);
    ctx.fillStyle=color+"33";ctx.fill();
    ctx.strokeStyle=color;ctx.lineWidth=4;ctx.stroke();
    ctx.fillStyle=color;ctx.font="bold 16px Arial";
    ctx.fillText(Math.round(status.angle)+"deg",x+18,y-10);
    ctx.fillStyle="#FFD700";ctx.font="13px Arial";
    ctx.fillText("ideal:"+status.ideal+"deg",x+18,y+12);
  }
}

/// Servo tracking
let lastServoCall = 0;
const SERVO_COOLDOWN = 600;
const CENTER_ZONE = 0.12;
let noPersonCount = 0;
let searchDirection = 1;
let searchStep = 0;

function searchForPerson() {
  const now = Date.now();
  if (now - lastServoCall < SERVO_COOLDOWN) return;
  lastServoCall = now;

  // Search pattern: pan left/right slowly
  if (searchStep < 3) {
    fetch(`/servo?pan=right&tilt=90`).catch(()=>{});
  } else if (searchStep < 6) {
    fetch(`/servo?pan=left&tilt=90`).catch(()=>{});
  } else {
    searchStep = 0;
    return;
  }
  searchStep++;
  setTimeout(() => fetch('/servo?pan=stop&tilt=90').catch(()=>{}), 400);
}

function trackWithServos(landmarks) {
  const now = Date.now();
  if (now - lastServoCall < SERVO_COOLDOWN) return true;

  const ls = landmarks[11], rs = landmarks[12];
  const lh = landmarks[23], rh = landmarks[24];

  const cx = (ls.x + rs.x + lh.x + rh.x) / 4;
  const cy = (ls.y + rs.y + lh.y + rh.y) / 4;

  let panDir = 'stop';
  let tiltAngle = 90;
  let isCentered = true;

  // Pan control - horizontal centering
  if (cx < 0.5 - CENTER_ZONE) {
    panDir = 'left';
    isCentered = false;
  } else if (cx > 0.5 + CENTER_ZONE) {
    panDir = 'right';
    isCentered = false;
  }

  // Tilt control - only move if significantly off center
  // Map cy to tilt angle carefully to avoid extreme movements
  if (cy < 0.25) {
    tiltAngle = 65;  // slightly up
    isCentered = false;
  } else if (cy > 0.75) {
    tiltAngle = 115; // slightly down
    isCentered = false;
  } else {
    tiltAngle = 90;  // stay center
  }

  fetch(`/servo?pan=${panDir}&tilt=${tiltAngle}`).catch(()=>{});
  if (!isCentered) {
    setTimeout(() => fetch('/servo?pan=stop&tilt=90').catch(()=>{}), 350);
  }
  lastServoCall = now;
  noPersonCount = 0;
  searchStep = 0;
  return isCentered;
}

function detect(){
  if(img.complete&&img.naturalWidth>0&&poseLandmarker){
    const W=canvas.width,H=canvas.height;
    ctx.clearRect(0,0,W,H);
    ctx.drawImage(img,0,0,W,H);
    try{
      const r=poseLandmarker.detect(img);
      if(r.landmarks&&r.landmarks.length>0){
        const lm=r.landmarks[0];
        const isCentered=trackWithServos(lm);
        drawingUtils.drawConnectors(lm,PoseLandmarker.POSE_CONNECTIONS,{color:"#00D1FF",lineWidth:3});
        drawingUtils.drawLandmarks(lm,{color:"#00D1FF",radius:6});
        if(!isCentered){
          exerciseEl.textContent="Centering...";
          feedbackEl.textContent="Move to center of frame!";
          feedbackEl.className="card-value";
        } else {
          const result=tracker.update(lm);
          if(result.jointStatus&&Object.keys(result.jointStatus).length>0){
            drawIdealPose(lm,result.exercise,result.joiantStatus);
          }
          repsEl.textContent=result.count;
          angleEl.textContent=result.angle;
          exerciseEl.textContent=result.exercise;
          feedbackEl.textContent=result.feedback||"-";
          const isGood=result.feedback&&(result.feedback.includes("Good")||result.feedback.includes("Perfect")||result.feedback.includes("Great"));
          feedbackEl.className="card-value"+(isGood?" good":"");
        }
      }
    } catch(e) {}
  } else {
    // No person detected - search!
    noPersonCount++;
    if (noPersonCount > 10) {
      searchForPerson();
      exerciseEl.textContent = "Searching...";
      feedbackEl.textContent = "No person detected - searching...";
    }
  }
  setTimeout(detect, 100);
}
async function setup(){
  const vision=await FilesetResolver.forVisionTasks("https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision/wasm");
  poseLandmarker=await PoseLandmarker.createFromOptions(vision,{
    baseOptions:{modelAssetPath:"https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task",delegate:"GPU"},
    runningMode:"IMAGE",numPoses:1
  });
  drawingUtils=new DrawingUtils(ctx);
  statusEl.textContent="AI Ready!";
  detect();
}
setup().catch(err=>{statusEl.textContent="Error: "+err.message;});
</script>
</body>
</html>'''

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/servo'):
            params = parse_qs(urlparse(self.path).query)
            pan_dir = params.get('pan', ['stop'])[0]
            tilt_angle = params.get('tilt', [None])[0]
            tilt_val = int(tilt_angle) if tilt_angle else None
            send_servo(pan_dir, tilt_val)
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(b'OK')
            return
        if self.path == '/stream':
            self.send_response(200)
            self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=frame')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            while True:
                with lock:
                    frame = latest_frame
                if frame:
                    try:
                        self.wfile.write(b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                    except:
                        break
                time.sleep(0.033)
        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(HTML)
    def log_message(self, f, *a):
        pass

print("GymEye running on port 5000")
from http.server import ThreadingHTTPServer
ThreadingHTTPServer(('0.0.0.0', 5000), Handler).serve_forever()