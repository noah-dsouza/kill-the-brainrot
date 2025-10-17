# hand_control.py
import cv2
import mediapipe as mp
import time
import numpy as np

class HandController:
    def __init__(self, cam_index=0):
        self.cam_index = cam_index
        self.running = False
        self.cap = None

        self._mp_hands = mp.solutions.hands
        self._mp_draw = mp.solutions.drawing_utils
        self._mp_styles = mp.solutions.drawing_styles
        self._hands = self._mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        self.x = 0.5
        self.y = 0.5
        self.click_pending = False
        self.last_click_time = 0
        self.prev_fist = False

    def start(self):
        self.cap = cv2.VideoCapture(self.cam_index)
        if not self.cap.isOpened():
            raise RuntimeError("Camera not accessible — check macOS permissions.")
        self.running = True
        print("Hand tracking started (embedded mode)")

    def update(self):
        """Returns (frame, x, y, click_detected)"""
        if not self.running:
            return None, self.x, self.y, False

        ret, frame = self.cap.read()
        if not ret:
            return None, self.x, self.y, False

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self._hands.process(rgb)

        fist_now = False
        if result.multi_hand_landmarks:
            hand_landmarks = result.multi_hand_landmarks[0]
            self._mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                self._mp_hands.HAND_CONNECTIONS,
                self._mp_styles.get_default_hand_landmarks_style(),
                self._mp_styles.get_default_hand_connections_style()
            )

            # wrist position
            self.x = hand_landmarks.landmark[0].x
            self.y = hand_landmarks.landmark[0].y

            fist_now = self._is_fist(hand_landmarks, w, h)
            if fist_now and not self.prev_fist and (time.time() - self.last_click_time) > 0.4:
                self.click_pending = True
                self.last_click_time = time.time()
            self.prev_fist = fist_now

        # BGR → RGB for pygame
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_rgb = np.rot90(frame_rgb)  
        frame_surface = None
        try:
            import pygame
            frame_surface = pygame.surfarray.make_surface(frame_rgb)
        except Exception:
            pass

        click_now = False
        if self.click_pending:
            self.click_pending = False
            click_now = True

        return frame_surface, self.x, self.y, click_now

    def _is_fist(self, lm, w, h):
        pts = [(int(p.x * w), int(p.y * h)) for p in lm.landmark]
        def extended(tip, pip): return pts[tip][1] < pts[pip][1] - 12
        thumb_ext = abs(pts[4][0] - pts[2][0]) > abs(pts[3][0] - pts[2][0]) + 10
        index_ext = extended(8, 6)
        middle_ext = extended(12, 10)
        ring_ext = extended(16, 14)
        pinky_ext = extended(20, 18)
        extended_count = sum([thumb_ext, index_ext, middle_ext, ring_ext, pinky_ext])
        return extended_count <= 1

    def stop(self):
        self.running = False
        if self.cap:
            self.cap.release()
        self._hands.close()
        print("Hand tracking stopped")
