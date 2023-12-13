from feat import Detector
import numpy as np
import cv2
import os
import pandas as pd
from pprint import pprint
#Part 1.


df = pd.read_csv("DiffusionFER/dataset_sheet.csv")
detector = Detector(device="cpu")

au_data = []
for i, row in df.iterrows():

    img_path = "DiffusionFER/" + row["subDirectory_filePath"]
    filename = os.path.basename(img_path)
    if not os.path.exists(img_path):
        print("Image not found: ", img_path)
        continue

    image = cv2.imread(img_path)
    predictions = detector.detect_image(img_path)

    #2.
    for i, pred in predictions.iterrows():
        try:
            x, y, w, h, _ = np.array(pred.faceboxes).astype(int)
        except:
            print("face not detected: ", img_path)
            break
        top_emotion = pred.emotions.sort_values(ascending=False).index[0]
      
        new_row = {}
        for au,value in pred.aus.items():
            new_row[au] = value

        new_row.update(row.to_dict())
        au_data.append(new_row)

new_df = pd.DataFrame(au_data)
new_df.to_csv("DiffusionFER/au_data.csv", index=False)