import cv2
import time
import json
import requests
import sys
from collections import defaultdict, deque
from pathlib import Path
from sql_record import sql_input_select

# Network addresses now come from the shared config file, so changing a board's
# IP means editing public_variable.py only. See section 8 of the README.
# 網絡位址統一由共用設定檔提供，換 IP 只需改 public_variable.py。詳見 README 第 8 節。
from public_variable import DOOR_ESP_IP, ESP32_URL

# ==================================
CAMERA_STREAM = ESP32_URL        # camera node stream / 鏡頭節點串流
MODEL_PATH = Path("model.yml")
LABELS_PATH = Path("labels.json")
DATA_INPUT = True

# Recognizing parameters
# NOTE: these are the values the shipped recognition loop actually uses. They
# intentionally mirror public_variable.py so the two files cannot drift apart.
# 注意：以下是實際運作時使用的值。刻意與 public_variable.py 保持一致，避免兩份設定分歧。
CONFIDENCE_THRESHOLD = 50
REQUIRED_COUNT = 10    # x, success x times in y seconds / y 秒內成功 x 次
WINDOW_TIME = 4.0      # y, success x times in y seconds / 投票視窗秒數

# ==================================

def trigger_esp32_unlock(name):
    """sending HTTP asking ESP32 unlock..."""
    
    try:
        print(f"\n[Door Lock System] success: {name}, sending unlock signal...")
        
        url = f"http://{DOOR_ESP_IP}/on"
        res = requests.get(url, timeout=2)
        if res.status_code == 200:
            
            print(">> [success] Door is now unlocked")

    except Exception as e:
        print(f">> [Error] unsuccessful connecting ESP32: {e}")

class TrackedFace:
    def __init__(self, tracker, bbox, start_frame):
        self.tracker = tracker
        self.bbox = bbox  # (x, y, w, h)
        self.last_seen = start_frame
        self.recog_log = deque()
        self.name = "Scanning..."

    def update(self, frame, frame_idx):
        success, box = self.tracker.update(frame)
        if success:
            self.bbox = tuple(map(int, box))
            self.last_seen = frame_idx
        return success

def load_resources():
    if not MODEL_PATH.exists() or not LABELS_PATH.exists():
        print("error: model.yml or labels.json are not found")
        sys.exit(1)
    
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(str(MODEL_PATH))
    with open(LABELS_PATH, "r") as f:
        id2name = {int(v): k for k, v in json.load(f).items()}
    return recognizer, id2name

def main(record):
    
    recognizer, id2name = load_resources()
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    cap = cv2.VideoCapture(CAMERA_STREAM)

    tracked_faces = {} # {id: TrackedFace}
    face_id_counter = 0
    frame_count = 0

    print(f"Starting up ... Camera stream: {CAMERA_STREAM}")

    while True:
        ret, frame = cap.read()
        if not ret: continue
        
        frame_count += 1
        display_frame = frame.copy()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # 1. upadate the tracking
        lost_ids = []
        for fid, tf in tracked_faces.items():
            if not tf.update(frame, frame_count) or (frame_count - tf.last_seen > 30):
                lost_ids.append(fid)
            else:
                # Recognizing
                tx, ty, tw, th = tf.bbox
                if tx > 0 and ty > 0 and tx+tw < frame.shape[1] and ty+th < frame.shape[0]:
                    face_roi = cv2.resize(gray[ty:ty+th, tx:tx+tw], (200, 200))
                    label, conf = recognizer.predict(face_roi)
                    
                    if conf < CONFIDENCE_THRESHOLD:
                        current_name = id2name.get(label, "Unknown")
                        now = time.time()
                        tf.recog_log.append(now)
                        # Remove the record outside the window
                        while tf.recog_log and now - tf.recog_log[0] > WINDOW_TIME:
                            tf.recog_log.popleft()
                        
                        tf.name = f"{current_name} ({len(tf.recog_log)})"
                        
                        # trigger the lock
                        if len(tf.recog_log) >= REQUIRED_COUNT:
                            if DATA_INPUT ==True:
                                trigger_esp32_unlock(current_name)
                                if record == True:
                                    sql_input_select(current_name)
                                    record = False
                                #sql_input_select(current_name)
                                tf.recog_log.clear() # prevent continusly triggering
                                Data_input = False
                    else:
                        tf.name = "Unknown"

                # tracking box of human face
                cv2.rectangle(display_frame, (tx, ty), (tx+tw, ty+th), (0, 255, 0), 2)
                cv2.putText(display_frame, tf.name, (tx, ty-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        for fid in lost_ids: del tracked_faces[fid]

        # 2. detect and check for a new face in every 10 frame
        if frame_count % 10 == 0: # 10(in frame)
            faces = face_cascade.detectMultiScale(gray, 1.2, 5, minSize=(80,80))
            for (x, y, w, h) in faces:
                # check whether it is already tracking
                is_new = True
                for tf in tracked_faces.values():
                    tx, ty, tw, th = tf.bbox
                    if max(x, tx) < min(x+w, tx+tw) and max(y, ty) < min(y+h, ty+th):
                        is_new = False
                        break
                
                if is_new:
                    # MOSSE tracking
                    tracker = cv2.legacy.TrackerMOSSE_create()
                    tracker.init(frame, (x, y, w, h))
                    tracked_faces[face_id_counter] = TrackedFace(tracker, (x, y, w, h), frame_count)
                    face_id_counter += 1

        cv2.imshow("Smart Door Lock System", display_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'): break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    record = True
    main(record)