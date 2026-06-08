"""
Cyra-OS Vision System v2
OpenCV webcam with Haar face detection, better error handling, status reporting.
"""
import cv2
import threading
import time
import base64
from pathlib import Path


class VisionSystem:
    def __init__(self):
        self.cap = None
        self.running = False
        self.thread = None
        self.latest_frame = None
        self.face_visible = False
        self._lock = threading.Lock()
        self.error = None
        self.face_cascade = None
        self._load_cascade()

    def _load_cascade(self):
        try:
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
            if self.face_cascade.empty():
                self.error = "Face cascade loaded but empty"
        except Exception as e:
            self.error = f"Face cascade load failed: {e}"

    def start(self):
        """Start webcam capture. Returns True on success."""
        try:
            self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            if not self.cap.isOpened():
                self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                self.error = "No webcam found"
                return False

            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
            self.running = True
            self.thread = threading.Thread(target=self._loop, daemon=True)
            self.thread.start()
            self.error = None
            return True
        except Exception as e:
            self.error = str(e)
            return False

    def _loop(self):
        while self.running:
            try:
                ret, frame = self.cap.read()
                if ret:
                    with self._lock:
                        # Face detection
                        if self.face_cascade and not self.face_cascade.empty():
                            try:
                                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                                faces = self.face_cascade.detectMultiScale(gray, 1.1, 5)
                                self.face_visible = len(faces) > 0
                                for (x, y, w, h) in faces:
                                    cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 255, 255), 1)
                            except:
                                pass
                        self.latest_frame = frame
                else:
                    time.sleep(0.1)
            except Exception as e:
                self.error = str(e)
                time.sleep(0.5)
            time.sleep(0.05)

    def get_frame_jpeg(self):
        with self._lock:
            if self.latest_frame is None:
                return None
            try:
                _, buf = cv2.imencode('.jpg', self.latest_frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
                return base64.b64encode(buf).decode()
            except:
                return None

    def get_status(self):
        return {
            "running": self.running,
            "face_visible": self.face_visible,
            "error": self.error,
            "has_frame": self.latest_frame is not None
        }

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        if self.cap:
            self.cap.release()
            self.cap = None


vision = VisionSystem()
