# delete_user.py
import argparse
from pathlib import Path
import json
import subprocess
import sys
import shutil

#import variables
from public_variable import CAM_INDEX, MODEL_PATH, LABELS_PATH, IMG_SIZE, CASCADE, RECOG_INTERVAL_FRAMES, CONFIDENCE_THRESHOLD, IMAGES_DIR, PROCESSED_DIR, WINDOW_TIME, REQUIRED_COUNT


# --- path (if change) ---
# Derived from BASE_DIR (see public_variable.py), so this works from any clone.
# 由 BASE_DIR 推算（見 public_variable.py），因此在任何 clone 位置都能運作。
PROCESS_AND_TRAIN_SCRIPT = Path(__file__).resolve().parent / "process_and_train.py"
# -------------------------------------

def backup(path: Path):
    if not path.exists():
        return None
    dest = path.parent / (path.name + "_backup")
    # if backup exist, avoid cover the original one -> add numbers at the back
    i = 0
    final_dest = dest
    while final_dest.exists():
        i += 1
        final_dest = Path(str(dest) + f"_{i}")
    if path.is_file():
        shutil.copy2(path, final_dest)
    else:
        shutil.copytree(path, final_dest)
    return final_dest

def delete_user_files(name: str):
    deleted = {"images": [], "processed": []}
    # raw images: the file name is: name_timestamp_idx.ext /or/ name_*.*
    if IMAGES_DIR.exists():
        for p in list(IMAGES_DIR.glob(f"{name}_*")):
            try:
                p.unlink()
                deleted["images"].append(str(p))
            except Exception as e:
                print(f"delete {p} fail: {e}")
    else:
        print(f"Warning!:Images not existing: {IMAGES_DIR}")

    # processed images
    if PROCESSED_DIR.exists():
        for p in list(PROCESSED_DIR.glob(f"{name}_*")):
            try:
                p.unlink()
                deleted["processed"].append(str(p))
            except Exception as e:
                print(f"delete {p} fail: {e}")
    else:
        print(f"Warning!:Images not existing: {PROCESSED_DIR}")

    return deleted

def update_labels_json_remove(name: str):
    if not LABELS_PATH.exists():
        print("labels.json not exist, update labels first")
        return False
    try:
        with open(LABELS_PATH, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except Exception as e:
        print("read labels.json fail:", e)
        return False

    # find the deleted key(s)（keys can be "name"）
    removed = []
    keys = list(data.keys())
    for k in keys:
        if k == name:
            removed.append(k)
            data.pop(k, None)

    if not removed:
        print(f"labels.json can't find name = '{name}' , no action")
        return False

    # store the latest labels.json
    try:
        with open(LABELS_PATH, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
        print(f"labels.json removed: {removed}")
        return True
    except Exception as e:
        print("write in labels.json fail:", e)
        return False

def call_retrain():
    # if process_and_train.py exist, call it
    if PROCESS_AND_TRAIN_SCRIPT.exists():
        print("Start running process_and_train.py to retrain the model...\n" \
        "----------------------------------------------------------------------")
        try:
            # use the same python environment to call and run
            res = subprocess.run([sys.executable, str(PROCESS_AND_TRAIN_SCRIPT)], check=False)
            if res.returncode == 0:
                print("retrain done")
            else:
                print(f"retrain finish, but returncode = {res.returncode}, please check the output of process_and_train.py")
        except Exception as e:
            print("Calling process_and_train.py error:", e)
    else:
        print("Cannot find file:  process_and_train.py, please check model.yml and labels.json。")

def main():
    parser = argparse.ArgumentParser(description="delete face data from the system of some one (Images, Images_processed, labels.json)。")
    parser.add_argument("--name", required=True, help="the name of the user going to remove (such as: alex_)")
    parser.add_argument("--backup", action="store_true", help="need backup Images and Images_processed (default false)")
    parser.add_argument("--retrain", action="store_true", help="call process_and_train.py after remove? retrain the modol")
    args = parser.parse_args()

    name = args.name.strip()
    if not name:
        print("error:name cannot be empty。")
        return

    # backup
    if args.backup:
        print("starting backup...(need some time)")
        b1 = backup(IMAGES_DIR) if IMAGES_DIR.exists() else None
        b2 = backup(PROCESSED_DIR) if PROCESSED_DIR.exists() else None
        if b1: print(f"Images backup to: {b1}")
        if b2: print(f"Images_processed backup to: {b2}")

    # delete files
    deleted = delete_user_files(name)
    print(f"delete raw images: {len(deleted['images'])} , delete processed images: {len(deleted['processed'])}")

    # update labels.json (if yes)
    updated = update_labels_json_remove(name)

    # if need retrain ,call process_and_train.py
    if args.retrain:
        call_retrain()
    else:
        if updated:
            print("modify labels.json, but model.yml still point to old model, please retrain")

if __name__ == "__main__":
    main()
