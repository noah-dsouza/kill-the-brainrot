# hand_control.py
import cv2
import mediapipe as mp
import time
import numpy as np

# DIRECT PATH IMPORTS (This is the magic for your Mac)
try:
    from mediapipe.python.solutions import hands as mp_hands
    from mediapipe.python.solutions import drawing_utils as mp_drawing
    from mediapipe.python.solutions import drawing_styles as mp_styles
except ImportError:
    import mediapipe.solutions.hands as mp_hands
    import mediapipe.solutions.drawing_utils as mp_drawing
    import mediapipe.solutions.drawing_styles as mp_styles

class HandController:
    def __init__(self, cam_index=0):
        self.cam_index = cam_index
        self.running = False
        self.cap = None

        # Pointing directly to the imported modules
        self._mp_hands = mp_hands
        self._mp_draw = mp_drawing
        self._mp_styles = mp_styles
        
        self._hands = self._mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        self.x, self.y = 0.5, 0.5
        self.click_pending = False
        self.last_click_time = 0
        self.prev_fist = False

    def start(self):
        self.cap = cv2.VideoCapture(self.cam_index)
        if not self.cap.isOpened():
            raise RuntimeError("Camera not accessible.")
        self.running = True
        print("Hand tracking started (Mac Fix Active)")

    def update(self):
        if not self.running: return None, self.x, self.y, False
        ret, frame = self.cap.read()
        if not ret: return None, self.x, self.y, False

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self._hands.process(rgb)

        fist_now = False
        if result.multi_hand_landmarks:
            hand_landmarks = result.multi_hand_landmarks[0]
            self._mp_draw.draw_landmarks(
                frame, hand_landmarks, self._mp_hands.HAND_CONNECTIONS,
                self._mp_styles.get_default_hand_landmarks_style(),
                self._mp_styles.get_default_hand_connections_style()
            )
            self.x, self.y = hand_landmarks.landmark[0].x, hand_landmarks.landmark[0].y
            fist_now = self._is_fist(hand_landmarks, w, h)
            if fist_now and not self.prev_fist and (time.time() - self.last_click_time) > 0.4:
                self.click_pending = True
                self.last_click_time = time.time()
            self.prev_fist = fist_now

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_rgb = np.rot90(frame_rgb)  
        try:
            import pygame
            frame_surface = pygame.surfarray.make_surface(frame_rgb)
        except: frame_surface = None

        click_now = self.click_pending
        self.click_pending = False
        return frame_surface, self.x, self.y, click_now

    def _is_fist(self, lm, w, h):
        pts = [(int(p.x * w), int(p.y * h)) for p in lm.landmark]
        def ext(tip, pip): return pts[tip][1] < pts[pip][1] - 12
        count = sum([abs(pts[4][0]-pts[2][0]) > abs(pts[3][0]-pts[2][0])+10, ext(8,6), ext(12,10), ext(16,14), ext(20,18)])
        return count <= 1

    def stop(self):
        self.running = False
        if self.cap: self.cap.release()
        self._hands.close()
