import cv2
from . import mp_drawing, mp_hands

def count_fingers(hand_landmarks, handedness):
    fingers = []
    
    # Thumb detection
    thumb_tip = hand_landmarks.landmark[4]
    thumb_base = hand_landmarks.landmark[2]
    
    if handedness == "Right":
        fingers.append(1 if thumb_tip.x < thumb_base.x else 0)
    else:
        fingers.append(1 if thumb_tip.x > thumb_base.x else 0)
    
    # Other fingers
    for tip, pip in [(8,6), (12,10), (16,14), (20,18)]:
        fingers.append(1 if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[pip].y else 0)
    
    return sum(fingers)

def count_fingers_in_frame(frame):
    with mp_hands.Hands(
        min_detection_confidence=0.8,
        min_tracking_confidence=0.5,
        max_num_hands=2
    ) as hands:
        
        # Convert and flip
        image = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        
        # Process detection
        results = hands.process(image)
        image.flags.writeable = True
        processed_frame = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        total_fingers = 0
        
        if results.multi_hand_landmarks:
            for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                mp_drawing.draw_landmarks(
                    processed_frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS
                )
                
                handedness = results.multi_handedness[idx].classification[0].label
                total_fingers += count_fingers(hand_landmarks, handedness)
        
        return processed_frame, total_fingers  # Now returns both values