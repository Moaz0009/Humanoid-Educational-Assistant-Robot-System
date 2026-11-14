import tensorflow as tf
import keras
import numpy as np
import cv2
from tensorflow.keras.models import load_model
from tensorflow.keras import backend as K

# Solving TF and Pytorch GPU Conflict
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
    except RuntimeError as e:
        print(e)

        
def triplet_loss(y_true, y_pred, alpha = 0.2):
    """
    Implementation of the triplet loss as defined by formula (3)
    
    Arguments:
    y_true -- true labels, required when you define a loss in Keras, you don't need it in this function.
    y_pred -- python list containing three objects:
            anchor -- the encodings for the anchor images, of shape (None, 128)
            positive -- the encodings for the positive images, of shape (None, 128)
            negative -- the encodings for the negative images, of shape (None, 128)
    
    Returns:
    loss -- real number, value of the loss
    """
    anchor, positive, negative = y_pred[0], y_pred[1], y_pred[2]
    pos_dist = tf.reduce_sum(tf.square(anchor - positive), axis = -1)
    neg_dist = tf.reduce_sum(tf.square(anchor - negative), axis = -1)
    basic_loss = pos_dist- neg_dist + alpha
    loss = tf.reduce_sum(tf.maximum(basic_loss, 0.0))
    return loss

face_cascade_path = '/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml'
face_cascade = cv2.CascadeClassifier(face_cascade_path)
FRmodel = load_model('/home/jetson-nx/Robot_System/Face_Detection/MODEL_SAV',custom_objects={'triplet_loss':triplet_loss,'K':K})

    
def img_to_encoding(image, model):
    image = np.array(image, dtype=np.float32)
    if image.shape[:2] != (96, 96):
        image = tf.image.resize(image, (96, 96))
    img = np.around(np.transpose(image, (2, 0, 1)) / 255.0, decimals=12)
    x_train = np.expand_dims(img, axis=0)
    #print(x_train.shape)
    embedding = model.predict(x_train)
    return embedding


