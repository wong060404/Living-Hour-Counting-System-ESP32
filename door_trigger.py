# door_control.py
import time
from collections import defaultdict, deque

class DoorControl:
    def __init__(self, time_window=4, threshold=10):
        self.time_window = time_window
        self.threshold = threshold
        self.recognition_log = defaultdict(deque)  # {person_name: deque[timestamps]}

    def record_recognition(self, person_name):
        """記錄一次人臉識別成功"""
        now = time.time()
        log = self.recognition_log[person_name]

        # 新紀錄入列
        log.append(now)

        # 移除超出 time_window 的紀錄
        while log and now - log[0] > self.time_window:
            log.popleft()

        # 判斷是否達成開門條件
        if len(log) >= self.threshold:
            self.open_door(person_name)
            log.clear()  # 清空，避免短時間內重複觸發

    def open_door(self, person_name):
        """模擬發送開門信號給硬體"""
        print(f"[門禁] {person_name} 在 {self.time_window} 秒內被確認 {self.threshold} 次 ✅ 觸發開門信號！")
        # TODO: 這裡可以改成實際硬體控制，例如：
        # GPIO.output(RELAY_PIN, GPIO.HIGH)
        # time.sleep(1)
        # GPIO.output(RELAY_PIN, GPIO.LOW)
