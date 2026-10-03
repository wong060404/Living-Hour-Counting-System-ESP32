#public_variable.py
import cv2
from pathlib import Path

# ---------------------------------------------------------------------------
# This file is the SINGLE SOURCE OF TRUTH for paths and network addresses.
# 本檔案是路徑與網絡位址的唯一真實來源。
#
# BASE_DIR resolves to the folder this file lives in, so a fresh clone works
# with NO editing at all. If you want to store the face data somewhere else
# (an external drive, a network share), replace the line below with an
# explicit path -- and use forward slashes "/" even on Windows, because a
# trailing backslash inside a Python string starts an escape sequence (the
# classic "\U" problem).
#
# BASE_DIR 會自動指向本檔案所在的資料夾，所以全新 clone 後無需任何修改即可運作。
# 若想把人臉資料存到別處（外接硬碟、網絡磁碟），請把下面那行改成明確路徑 ——
# 即使在 Windows 也請用正斜線 "/"，因為 Python 字串中的反斜線會觸發轉義。
#
#   BASE_DIR = Path(r"C:/Users/yourname/Downloads/Living-Hour-Counting-System-ESP32")
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent

# path of raw face
IMAGES_DIR = BASE_DIR / "Images"

# path of processed face
PROCESSED_DIR = BASE_DIR / "Images_processed"

# data after trained
MODEL_PATH = BASE_DIR / "model.yml"

# (name <-> id)
LABELS_PATH = BASE_DIR / "labels.json"

# default camera idex (0) --> 1 for other camera
# 預設鏡頭編號（0）；使用其他鏡頭時改為 1
ESP32_URL = "http://192.168.5.1:81/stream"  # ESP32-CAM stream / 鏡頭節點串流
CAM_INDEX = 0                               # 0 = this PC's webcam / 本機鏡頭
DOOR_ESP_IP = "192.168.5.2"                 # relay node (door) / 繼電器節點（門）

# face recognize index
IMG_SIZE = (200, 200)  # face resize size
CASCADE = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# Recognizing parameters
RECOG_INTERVAL_FRAMES = 10   # times per frames
CONFIDENCE_THRESHOLD = 50    # confidence (LBPH: 越小越好 / lower is a better match)

# Check time and true times required
WINDOW_TIME = 4.0           # Time required (in Seconds) / 投票視窗秒數
REQUIRED_COUNT = 10         # "True" times required in limited time / 視窗內需成功次數

# ---------------------------------------------------------------------------
# Every path below is derived from BASE_DIR -- do not hard-code absolute paths.
# 以下所有路徑都由 BASE_DIR 推算，請勿寫死絕對路徑。
#
# Order matters: Control_System.py indexes this list by its menu number.
# 次序很重要：Control_System.py 以選單編號索引此清單。
# ---------------------------------------------------------------------------
FunFileL = [
    str(BASE_DIR / "capture.py"),             # menu 1 / 選單 1
    str(BASE_DIR / "process_and_train.py"),   # menu 2 / 選單 2
    str(BASE_DIR / "track_and_recognize.py"), # menu 3 / 選單 3
    str(BASE_DIR / "delete_user.py"),         # menu 4 & 5 / 選單 4、5
    str(BASE_DIR / "compare.py"),             # menu 6 / 選單 6
    str(BASE_DIR / "room_time.py"),           # menu 7 / 選單 7
    str(BASE_DIR / "check_report.py"),        # menu 8 / 選單 8
]