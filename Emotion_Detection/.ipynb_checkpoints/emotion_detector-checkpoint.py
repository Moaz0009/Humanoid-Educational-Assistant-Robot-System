import cv2
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

# Load model and initialize face detector
model = load_model('Emotion_Detection/face_model.h5')
class_names = ['Angry', 'Disgusted', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']
face_cascade_path = '/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml'
face_cascade = cv2.CascadeClassifier(face_cascade_path)


def detect_emotions_in_frame(frame):
    """
    Processes frame and returns:
    - processed_frame: Frame with bounding boxes and emotion labels
    - emotions: List of detected emotions (empty if no faces)
    """
    frame = cv2.flip(frame, 1)  # Mirror effect
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(30, 30))
    
    emotions = []
    
    for (x, y, w, h) in faces:
        # Extract and preprocess face
        face_roi = frame[y:y+h, x:x+w]
        face_img = cv2.resize(face_roi, (48, 48))
        face_img = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
        face_img = image.img_to_array(face_img)
        face_img = np.expand_dims(face_img, axis=0)
        
        # Predict emotion
        predictions = model.predict(face_img)
        emotion = class_names[np.argmax(predictions)]
        emotions.append(emotion)
        
        # Draw annotations
        cv2.putText(frame, f'{emotion}', (x, y-10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
    
    return frame, emotions