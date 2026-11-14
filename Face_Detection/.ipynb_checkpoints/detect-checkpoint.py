from .utils import *


def detect_verify(frame,database):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))  
    faces_cord=dict()
    identity = "Unknown"
    for (x, y, w, h) in faces:
        face = frame[y:y + h, x:x + w]
        embedding = img_to_encoding(face, FRmodel)
        #embedding=np.array(embedding['output_0'])
        # Find the closest match in the database
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        
        min_dist = float("inf")
        for name, db_enc in database.items():
            dist = np.linalg.norm(embedding-db_enc)
            if dist < min_dist and dist < 0.7:  # Threshold for recognition
                min_dist = dist
                identity = str(name)
                break
        cv2.putText(frame, identity, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)
        faces_cord[identity] = [int(x),int(y),int(w),int(h)]
    return identity,frame
