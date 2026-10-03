#process_and_train.py
import cv2
import os
from pathlib import Path
import json
import numpy as np

#import variables
from public_variable import CAM_INDEX, MODEL_PATH, LABELS_PATH, IMG_SIZE, CASCADE, RECOG_INTERVAL_FRAMES, CONFIDENCE_THRESHOLD, IMAGES_DIR, PROCESSED_DIR



#from capture import IMAGES_DIR

#IMAGES_DIR = Path("/Users/alex_wcc/PycharmProjects/PythonProject/Images")
#PROCESSED_DIR = Path("/Users/alex_wcc/PycharmProjects/PythonProject/Images_processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

#MODEL_PATH = Path("/Users/alex_wcc/PycharmProjects/PythonProject/model.yml")
#LABELS_PATH = Path("/Users/alex_wcc/PycharmProjects/PythonProject/labels.json")

#CASCADE = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

#IMG_SIZE = (200, 200)  # LBPH（Gray scale）(Small scale would be better)

def preprocess_and_save():
    """
    read the image in IMAGES_DIR ,detect face -> gary scale -> resize -> store in PROCESSED_DIR
    send back mapping: label_name -> numeric_label
    """
    files = sorted(IMAGES_DIR.glob("*.jpg")) + sorted(IMAGES_DIR.glob("*.png"))
    label_map = {}  # name -> label_id
    current_label = 0
    out_list = []  # tuples (image_array, label_id)
    for f in files:
        fname = f.stem  # e.g. alex_1600000_0
        # use the first as name (until the first underscore)
        name = fname.split("_")[0]
        if name not in label_map:
            label_map[name] = current_label
            current_label += 1

        img = cv2.imread(str(f))
        if img is None:
            continue
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = CASCADE.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(80,80))
        if len(faces) == 0:
            # If it does not dectect a face, scale the entire image
            face = cv2.resize(gray, IMG_SIZE)
        else:
            x,y,w,h = faces[0]
            face = gray[y:y+h, x:x+w]
            face = cv2.resize(face, IMG_SIZE)

        label_id = label_map[name]
        out_file = PROCESSED_DIR / f"{name}_{f.stem}.png"
        cv2.imwrite(str(out_file), face)
        out_list.append((face, label_id))

    # Store label_map
    with open(LABELS_PATH, "w") as fh:
        json.dump(label_map, fh, indent=2, ensure_ascii=False)

    print(f"Preprocessed {len(out_list)} images. Labels: {label_map}")
    return out_list, label_map

def train_lbph(out_list):
    """
    Use LBPH train recognizer and stor in MODEL_PATH
    """
    if len(out_list) == 0:
        raise RuntimeError("There is no trained images, please capture a face first!")

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    X = [img for (img, label) in out_list]
    y = [label for (img, label) in out_list]
    recognizer.train(X, np.array(y))
    recognizer.write(str(MODEL_PATH))
    print(f"Model saved to {MODEL_PATH}")

if __name__ == "__main__":
    out_list, label_map = preprocess_and_save()
    train_lbph(out_list)
    print("Finish Trained")


# python process_and_train.py