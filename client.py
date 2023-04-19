import platform
import socket
import struct
import cv2  # OpenCV is used only for writing text on image (for testing).
from timers import *
from mycodecs import *

# Video resolution and framerate.
width, height, fps, crf = 800, 600, 30, '15'

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("Connecting to server...")
sock.connect(('127.0.0.1', 8000))

# Set up video capture.
print("Opening web cam...")
print("Platform:", platform.system())
if platform.system() == "Windows":
    print("Using DSHOW.")
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
else:
    cap = cv2.VideoCapture(0)
    
cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
cap.set(cv2.CAP_PROP_FPS, fps)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)

# Timers and counters for logs.
bytes_recv = TimedCounter("Bytes Received", lambda name, val : print(f"{name}: {int(val / 1024)} kb/s"))
fps_counter = TimedCounter("FPS")
frame_timer = PerfTimer("Frame Time")

# --------------------------------------------------------------------------------

print("Streaming...")
encoder = CodecContextEncoder(width, height, fps, crf)

# This encoder was for testing - don't use.
#encoder = ContainerEncoder(width, height, fps, crf)

while(cap.isOpened()):
    with frame_timer:
        # Capture the frame from the camera.
        ret, orig_frame = cap.read()
        cv2.imshow('Source Video', orig_frame)

        video_bytes = encoder.encode_bgr_to_bytes(orig_frame)

        if video_bytes is None:
            continue

        # Sometimes the encoder cant give us a valid image yet.
        if video_bytes is None:
            continue

        # Send bytes to server.
        size = struct.pack('<L', len(video_bytes))
        sock.sendall(size + video_bytes)

        bytes_recv.add(len(video_bytes))

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        fps_counter.add(1)



