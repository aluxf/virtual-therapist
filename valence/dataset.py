from feat import Detector
import numpy as np
import cv2
import os
import pandas as pd
from pprint import pprint

# Part 1.

# Read the dataset sheet into a pandas DataFrame
df = pd.read_csv("DiffusionFER/dataset_sheet.csv")

# Create an instance of the Detector class
detector = Detector(device="cpu")

# Initialize an empty list to store the AU data
au_data = []

# Iterate over each row in the DataFrame
for i, row in df.iterrows():

    # Get the image path from the dataset sheet
    img_path = "DiffusionFER/" + row["subDirectory_filePath"]
    filename = os.path.basename(img_path)

    # Check if the image exists
    if not os.path.exists(img_path):
        print("Image not found: ", img_path)
        continue

    # Read the image using OpenCV
    image = cv2.imread(img_path)

    # Detect facial features and emotions using the detector
    predictions = detector.detect_image(img_path)

    # Iterate over each prediction
    for i, pred in predictions.iterrows():
        try:
            # Get the coordinates of the detected face
            x, y, w, h, _ = np.array(pred.faceboxes).astype(int)
        except:
            print("Face not detected: ", img_path)
            break

        # Get the top emotion from the prediction
        top_emotion = pred.emotions.sort_values(ascending=False).index[0]

        # Create a new row to store the AU data
        new_row = {}

        # Iterate over each AU and its value
        for au, value in pred.aus.items():
            new_row[au] = value

        # Add the original row data to the new row
        new_row.update(row.to_dict())

        # Append the new row to the AU data list
        au_data.append(new_row)

# Create a new DataFrame from the AU data
new_df = pd.DataFrame(au_data)

# Save the new DataFrame to a CSV file
new_df.to_csv("DiffusionFER/au_data.csv", index=False)