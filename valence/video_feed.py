import cv2
from feat import Detector
from joblib import dump, load
from time import sleep
from multiprocessing import Process, Manager
from time import sleep
import numpy as np
import time
import os

import warnings
warnings.filterwarnings("ignore")

def display_camera_feed():
    # Create a detector object
    detector = Detector(device="mps")

    # Open the default camera with widht and height as 640x480
    cap = cv2.VideoCapture(0)
    cap.set(3, 640)
    cap.set(4, 480)

    while True:
        # Read the frame from the camera
        ret, frame = cap.read()

        # Detect the face and print the action units
        faces = detector.detect_faces(frame)
        landmarks = detector.detect_landmarks(frame, faces)
        aus = detector.detect_aus(frame, landmarks)
        print(aus)

        # Display the frame
        cv2.imshow('Camera Feed', frame)

        # Exit the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the camera and close the window
    cap.release()
    cv2.destroyAllWindows()

def get_valence(frame, detector, model):
    try:
        faces = detector.detect_faces(frame)
        if not faces[0]:
            return 0
        landmarks = detector.detect_landmarks(frame, faces)
        aus = detector.detect_aus(frame, landmarks)
        valence = model.predict(aus[0])[0]
    except Exception as e:
        print(e)
        return 0
    
    #process valence prediction
    return valence



def valence_feed(shared_list):

    """
    Feed the shared list with valence values obtained from video frames.
    FPS is limited to 2 frames per second because of the model inference time.

    Args:
        shared_list (list): A shared list to store valence values.

    Returns:
        int: Returns 0 if there was an error reading the frame from the camera.

    """
    detector = Detector(device="mps")
    cam = cv2.VideoCapture(0)
    __dir__ = os.path.dirname(os.path.abspath(__file__))

    model = load(__dir__ + '/valence_model.joblib')
    while True:
        t_start = time.time()
        ret, frame = cam.read()
        if not ret or frame is None:
            print("Failed to read frame from camera")
            return 0
        valence = get_valence(frame, detector, model)
        if valence is not None:
            if len(shared_list) >= 2:  # Check if the list is full
                shared_list.pop(0)  # Remove the oldest item
            shared_list.append(valence)  # Add the new item
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        t_end = time.time()
        sleep_time = 0.5 - (t_end - t_start)
        if sleep_time < 0:
            sleep_time = 0
        
        sleep(sleep_time)
    cam.release()

def consumer(shared_list):
    while True:
        if shared_list:
            print(shared_list)
            avg_valence = np.mean(shared_list)
            print(avg_valence)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        sleep(1)

