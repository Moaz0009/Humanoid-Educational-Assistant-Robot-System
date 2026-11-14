from .utils import *

def encode(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))  
    if len(faces) == 0:
        raise ValueError("No face detected. Please submit an image with a visible face.")
    elif len(faces) > 1:
        raise ValueError("Must submit an image of a single person.")
    else:
        x, y, w, h = faces[0]
        face = image[y:y + h, x:x + w]
        embedding = img_to_encoding(face, FRmodel)
        return embedding

def register_face(name,image_path,database):
    #url = "http://127.0.0.1:8000/upload_image"
    frame=cv2.imread(image_path)
   # _, img_encoded = cv2.imencode('.jpg', frame)
    img_encoded = encode(frame)
    database[name] = img_encoded
    return "Face Registerd Successfuly!"