import os
import cv2
import sys

# 1. Silences the duplicate library crashes
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

try:
    import mediapipe as mp
    # Manually pointing to the solutions if the shortcut is broken
    from mediapipe.python.solutions import hands as mp_hands
    from mediapipe.python.solutions import drawing_utils as mp_draw
    from mediapipe.python.solutions import drawing_styles as mp_styles
except ImportError:
    print("Error: Mediapipe isn't installed. Run 'pip install mediapipe'")
    sys.exit()

# 2. Initialize
detector = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5)
cap = cv2.VideoCapture(0)

print("Starting... Press 'q' to quit.")

while cap.isOpened():
    success, frame = cap.read()
    if not success: break

    # Flip and Convert
    frame = cv2.flip(frame, 1)
    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Process
    results = detector.process(img_rgb)

    # Draw
    if results.multi_hand_landmarks:
        for landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(
                frame, landmarks, mp_hands.HAND_CONNECTIONS,
                mp_styles.get_default_hand_landmarks_style(),
                mp_styles.get_default_hand_connections_style())

    cv2.imshow('Hand Tracker', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
