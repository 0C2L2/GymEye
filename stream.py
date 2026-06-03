import subprocess
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

latest_frame = b''
lock = threading.Lock()

def capture():
    global latest_frame
    proc = subprocess.Popen(
        ['ffmpeg', '-f', 'v4l2', '-framerate', '30',
         '-video_size', '640x480', '-i', '/dev/video0',
         '-vf', 'fps=30', '-vcodec', 'mjpeg', '-q:v', '3',
         '-f', 'image2pipe', '-update', '1', 'pipe:1'],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=0
    )
    buf = b''
    while True:
        chunk = proc.stdout.read(4096)
        if not chunk:
            break
        buf += chunk
        while True:
            start = buf.find(b'\xff\xd8')
            end = buf.find(b'\xff\xd9')
            if start != -1 and end != -1 and end > start:
                with lock:
                    latest_frame = buf[start:end+2]
                buf = buf[end+2:]
            else:
                break

threading.Thread(target=capture, daemon=True).start()
print("Waiting for camera...")
time.sleep(3)
print("Stream ready!")

class StreamHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/frame'):
            with lock:
                frame = latest_frame
            if not frame:
                self.send_response(503)
                self.end_headers()
                return
            self.send_response(200)
            self.send_header('Content-Type', 'image/jpeg')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            self.wfile.write(frame)
        else:
            self.send_response(200)
            self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=frame')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            while True:
                with lock:
                    frame = latest_frame
                if frame:
                    try:
                        self.wfile.write(b'--frame\r\n')
                        self.wfile.write(b'Content-Type: image/jpeg\r\n\r\n')
                        self.wfile.write(frame)
                        self.wfile.write(b'\r\n')
                    except:
                        break
                time.sleep(0.033)
    def log_message(self, format, *args):
        pass

print("Stream on port 5000")
HTTPServer(('0.0.0.0', 5000), StreamHandler).serve_forever()
