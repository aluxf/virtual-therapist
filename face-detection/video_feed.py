import cv2
from feat import Detector
from joblib import dump, load
from time import sleep

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

def get_valence(cam, detector, model):
    _, frame = cam.read()
    faces = detector.detect_faces(frame)
    if not faces[0]:
        return None
    landmarks = detector.detect_landmarks(frame, faces)
    aus = detector.detect_aus(frame, landmarks)
    valence = model.predict(aus[0])
    
    #process valence prediction
    return valence

if __name__ == '__main__':
    valence_model = load('valence_model.joblib')
    # Create a detector object
    detector = Detector(device="mps")

    cam = cv2.VideoCapture(0)

    while True:
        valence = get_valence(cam, detector, valence_model)
        print(valence)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        sleep(0.2)

    #display_camera_feed()
