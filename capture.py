#capture.py
import cv2
import os
from pathlib import Path
import time


#import variables
from public_variable import CAM_INDEX, MODEL_PATH, LABELS_PATH, IMG_SIZE, CASCADE, RECOG_INTERVAL_FRAMES, CONFIDENCE_THRESHOLD, IMAGES_DIR

CAM_INDEX = "http://192.168.5.1:81/stream"

#IMAGES_DIR = Path("/Users/alex_wcc/PycharmProjects/PythonProject/Images")
IMAGES_DIR.mkdir(parents=True, exist_ok=True)


#CASCADE = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

def capture_user_images(user_name: str, num_images: int = 30, delay_between: float = 0.2, cam_index: int = 0):
    """
    use webcam to capture photos of human face and store in  IMAGES_DIR
    format: <user_name>_<timestamp>_<idx>.jpg
    """
    
    #cap = cv2.VideoCapture(cam_index)
    if str(cam_index).isdigit():
        cam_index = int(cam_index)

    cap = cv2.VideoCapture(cam_index)

    if not cap.isOpened():
        raise RuntimeError("Cannot turn on the camera (index {}).".format(cam_index))

    captured = 0
    print(f"Start recognising {user_name},face to the camera. Press q to end early. target frame: {num_images}")
    while captured < num_images:
        ret, frame = cap.read()
        if not ret:
            print("camera read failed, retrying...")
            time.sleep(0.1)
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = CASCADE.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80))

        # Display the detected box
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x,y), (x+w, y+h), (255,0,0), 2)

        cv2.putText(frame, f"Captured: {captured}/{num_images}", (10,30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)
        cv2.imshow("Capture (press q to quit)", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

        # If detected the face, save the first photo
        if len(faces) > 0:
            x,y,w,h = faces[0]
            face_img = frame[y:y+h, x:x+w]
            timestamp = int(time.time())
            fname = IMAGES_DIR / f"{user_name}_{timestamp}_{captured}.jpg"
            cv2.imwrite(str(fname), face_img)
            captured += 1
            time.sleep(delay_between)

    cap.release()
    cv2.destroyAllWindows()
    print(f"Finish recognising, stored {captured} photos in {IMAGES_DIR}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True, help="user name")
    parser.add_argument("--num", type=int, default=30)
    parser.add_argument("--cam", default="0", help="camera index or stream URL")

    args = parser.parse_args()

    capture_user_images(
        args.name,
        num_images=args.num,
        cam_index=args.cam
    )

#Run format: python capture.py --name XXX --num 30 --cam 1
#.           python capture.py --name alex --num 30 --cam "http://192.168.5.1:81/stream"