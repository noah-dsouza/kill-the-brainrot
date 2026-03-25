# hand_control.py
import cv2
import time
import numpy as np
import os

import mediapipe as mp
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import (
    HandLandmarker,
    HandLandmarkerOptions,
    RunningMode,
)

# Hand landmark connections for drawing
HAND_CONNECTIONS = [
    (0,1),(1,2),(2,3),(3,4),
    (0,5),(5,6),(6,7),(7,8),
    (5,9),(9,10),(10,11),(11,12),
    (9,13),(13,14),(14,15),(15,16),
    (13,17),(17,18),(18,19),(19,20),(0,17),
]

MODEL_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task"
MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hand_landmarker.task")


def _ensure_model():
    if not os.path.exists(MODEL_PATH):
        print("Downloading hand landmarker model...")
        import urllib.request
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
        print("Model downloaded.")
    return MODEL_PATH


class HandController:
    def __init__(self, cam_index=0):
        self.cam_index = cam_index
        self.running = False
        self.cap = None

        model_path = _ensure_model()
        options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            running_mode=RunningMode.VIDEO,
            num_hands=1,
            min_hand_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        self._landmarker = HandLandmarker.create_from_options(options)
        self._frame_ts = 0

        self.x, self.y = 0.5, 0.5
        self.click_pending = False
        self.last_click_time = 0
        self.prev_fist = False

    def start(self):
        # Try the requested index first, then fallback alternatives
        for idx in [self.cam_index, 1, -1]:
            cap = cv2.VideoCapture(idx)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    self.cap = cap
                    self.running = True
                    print(f"Hand tracking started (camera index {idx})")
                    return
            cap.release()
        raise RuntimeError(
            "Camera not accessible. On macOS, grant camera permission to Terminal "
            "in System Settings > Privacy & Security > Camera."
        )

    def update(self):
        if not self.running:
            return None, self.x, self.y, False
        ret, frame = self.cap.read()
        if not ret:
            return None, self.x, self.y, False

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        self._frame_ts += 33  # ~30fps in ms
        result = self._landmarker.detect_for_video(mp_image, self._frame_ts)

        fist_now = False
        if result.hand_landmarks:
            landmarks = result.hand_landmarks[0]
            self._draw_landmarks(frame, landmarks, w, h)

            self.x = landmarks[0].x
            self.y = landmarks[0].y
            fist_now = self._is_fist(landmarks, w, h)
            if fist_now and not self.prev_fist and (time.time() - self.last_click_time) > 0.4:
                self.click_pending = True
                self.last_click_time = time.time()
            self.prev_fist = fist_now

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_rgb = np.rot90(frame_rgb)
        try:
            import pygame
            frame_surface = pygame.surfarray.make_surface(frame_rgb)
        except:
            frame_surface = None

        click_now = self.click_pending
        self.click_pending = False
        return frame_surface, self.x, self.y, click_now

    def _draw_landmarks(self, frame, landmarks, w, h):
        pts = [(int(lm.x * w), int(lm.y * h)) for lm in landmarks]
        for i, j in HAND_CONNECTIONS:
            cv2.line(frame, pts[i], pts[j], (0, 255, 0), 2)
        for pt in pts:
            cv2.circle(frame, pt, 4, (255, 0, 0), -1)

    def _is_fist(self, landmarks, w, h):
        pts = [(int(lm.x * w), int(lm.y * h)) for lm in landmarks]
        def ext(tip, pip):
            return pts[tip][1] < pts[pip][1] - 12
        count = sum([
            abs(pts[4][0] - pts[2][0]) > abs(pts[3][0] - pts[2][0]) + 10,
            ext(8, 6), ext(12, 10), ext(16, 14), ext(20, 18),
        ])
        return count <= 1

    def stop(self):
        self.running = False
        if self.cap:
            self.cap.release()
        self._landmarker.close()
