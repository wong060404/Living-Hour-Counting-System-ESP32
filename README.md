# Living Hour Counting System (ESP32)

### Public Housing Entrance Monitoring System · 公共房屋出入監測系統

**English** — A face-recognition door that logs who entered, when, and for how long — then reports the flats that fall below Hong Kong's 150-hour monthly occupancy rule.

**中文** — 一套人臉辨識門禁系統：記錄誰在甚麼時候進出、停留多久，然後列出每月居住時數低於香港 150 小時規定的單位。

Built as the *Project on Knowledge Product Development* (CCIT4080) final-year project at HKU SPACE Community College, Group CL11-01, Semester 2.

本專案為 HKU SPACE 社區書院工程學副學士 CCIT4080「知識產品開發專案」的畢業專題，組別 CL11-01，第二學期。

<p align="center">
  <img src="docs/images/architecture.png" alt="Three-tier architecture: hardware, Python processing layer, SQLite data layer / 三層架構：硬件、Python 處理層、SQLite 資料層" width="100%">
</p>

---

## Table of contents · 目錄

| English | 中文 |
|---|---|
| [1. What problem does this solve?](#1-what-problem-does-this-solve) | [這個專案解決甚麼問題？](#1-what-problem-does-this-solve) |
| [2. What the system actually does](#2-what-the-system-actually-does) | [系統實際做到甚麼](#2-what-the-system-actually-does) |
| [3. Architecture](#3-architecture) | [系統架構](#3-architecture) |
| [4. Bill of materials](#4-bill-of-materials) | [硬件清單](#4-bill-of-materials) |
| [5. Hardware assembly](#5-hardware-assembly) | [硬件組裝](#5-hardware-assembly) |
| [6. Flash the ESP32 boards](#6-flash-the-esp32-boards) | [燒錄 ESP32 開發板](#6-flash-the-esp32-boards) |
| [7. Software setup](#7-software-setup) | [軟件環境設定](#7-software-setup) |
| [8. Configure `public_variable.py`](#8-configure-public_variablepy) | [設定 `public_variable.py`](#8-configure-public_variablepy) |
| [9. Initialise the database](#9-initialise-the-database) | [初始化資料庫](#9-initialise-the-database) |
| [10. First run](#10-first-run) | [首次執行](#10-first-run) |
| [11. Daily operation](#11-daily-operation) | [日常操作](#11-daily-operation) |
| [12. The monthly reporting cycle](#12-the-monthly-reporting-cycle) | [每月報表流程](#12-the-monthly-reporting-cycle) |
| [13. Automate the monthly reset](#13-automate-the-monthly-reset) | [自動化每月重置](#13-automate-the-monthly-reset) |
| [14. Repository map](#14-repository-map) | [檔案地圖](#14-repository-map) |
| [15. Database schema](#15-database-schema) | [資料庫結構](#15-database-schema) |
| [16. Configuration reference](#16-configuration-reference) | [設定參數一覽](#16-configuration-reference) |
| [17. Troubleshooting](#17-troubleshooting) | [疑難排解](#17-troubleshooting) |
| [18. Privacy and data handling](#18-privacy-and-data-handling) | [私隱與資料處理](#18-privacy-and-data-handling) |
| [19. Known limitations and roadmap](#19-known-limitations-and-roadmap) | [已知限制與未來方向](#19-known-limitations-and-roadmap) |
| [20. Team and credits](#20-team-and-credits) | [團隊與鳴謝](#20-team-and-credits) |
| [Appendix: verifying the reports by hand](#appendix-verifying-the-reports-by-hand) | [附錄：手動核對報表](#appendix-verifying-the-reports-by-hand) |


---

## 1. What problem does this solve?

**English** — Hong Kong's public housing waiting list is long, yet some allocated flats sit empty or are used by somebody other than the registered tenant. The Housing Bureau can only act on suspicions it can evidence, and manual inspection is slow, intrusive and hard to scale.

This project is a **non-punitive evidence collector**. It does not lock anybody out for staying away. It answers one narrow question with data:

> For a given calendar month, how many hours was each registered flat actually occupied?

A single entrance camera identifies the resident as they come and go. Those events become timestamped rows in a local SQLite database. At month end, a script sums the entry/exit pairs into "resident hours", groups them into "flat hours", and prints every flat below **150 hours**. That list is what gets referred to a community centre or social worker for a supportive follow-up — not a penalty notice.

The **150-hour threshold** is a project policy default, not a legal figure. It is a single constant in `check_report.py` and is meant to be tuned by whoever operates the system.

**中文** — 香港公屋輪候冊很長，但部分已編配的單位卻長期空置，或由非登記住戶使用。房屋署只能就「有證據的懷疑」採取行動，而逐戶上門檢查既慢、擾民，又難以規模化。

本專案是一套**非懲罰性的證據收集工具**。它不會因為住戶長時間不在家就把人鎖在門外，而是用數據回答一條很窄的問題：

> 在某個曆月內，每個已登記單位實際上被居住了多少小時？

門口一支鏡頭在住戶出入時辨識其身分，這些事件會成為本機 SQLite 資料庫中帶時間戳的記錄。月結時，腳本把成對的出入時間相減得出「每人居住時數」，再按單位彙總成「每戶時數」，並列出所有低於 **150 小時**的單位。這份名單會轉介給社區中心或社工跟進，而非發出懲罰通知。

**150 小時只是本專案的政策預設值，並非法律規定。** 它是 `check_report.py` 裡的一個常數，實際運作者可按自己的政策調整。

---

## 2. What the system actually does

**English** — The table below is the honest capability list: what works, what does not, and where to find each part. Test status comes from the project's own seven scripted test cases.

**中文** — 下表是誠實的功能清單：哪些做得到、哪些做不到、各自的程式碼在哪。測試狀態來自專案本身的七個測試個案。

<p align="center">
  <img src="docs/images/data-flow.png" alt="End-to-end data flow from camera frame to database row / 由鏡頭畫面到資料庫記錄的完整資料流" width="100%">
</p>

| Capability · 功能 | Status · 狀態 | Where · 位置 |
|---|---|---|
| Register a resident by capturing 30 cropped face images<br>擷取 30 張人臉裁切影像以註冊住戶 | ✅ working · 已完成 | `capture.py` |
| Preprocess images and train an LBPH model<br>前處理影像並訓練 LBPH 模型 | ✅ working · 已完成 | `process_and_train.py` |
| Stream live video from an ESP32-S3-CAM over Wi-Fi<br>從 ESP32-S3-CAM 以 Wi-Fi 串流即時影像 | ✅ working · 已完成 | `public_variable.py`, `capture.py` |
| Detect faces with a Haar Cascade and follow them with a MOSSE tracker<br>用 Haar Cascade 偵測人臉、以 MOSSE 追蹤 | ✅ working · 已完成 | `track_and_recognize.py` |
| Recognise residents and label strangers as "Unknown"<br>辨識住戶，陌生人標示為 Unknown | ✅ working · 已完成 | `track_and_recognize.py` |
| Anti-false-positive voting (10 hits in a 4-second window)<br>防誤判投票（4 秒內 10 次成功） | ✅ working · 已完成 | `track_and_recognize.py` |
| Unlock a relay-driven electromagnetic lock over HTTP<br>以 HTTP 觸發繼電器電磁鎖開門 | ✅ working · 已完成 | `track_and_recognize.py` → `ESP_RELAY.py` |
| Log Entry/Leave timestamps into SQLite<br>將進出時間寫入 SQLite | ✅ working · 已完成 | `sql_record.py` |
| Monthly hours per resident and per flat<br>每月每人及每戶居住時數 | ✅ working · 已完成 | `compare.py`, `room_time.py` |
| Flag flats below 150 hours<br>標示低於 150 小時的單位 | ✅ working · 已完成 | `check_report.py` |
| Permanently remove a resident (images, labels, model)<br>徹底刪除住戶（影像、標籤、模型） | ✅ working · 已完成 | `delete_user.py` |
| Month-end rollover for residents who never left<br>跨月未離戶的自動結轉 | ✅ working · 已完成 | `reset.py` |
| Liveness / anti-spoofing (photo or phone held to camera)<br>活體偵測／防偽（用相片或手機屏幕欺騙鏡頭） | ❌ not implemented · 未實作 | — |
| Separate IN and OUT lanes (fixes the tailgating flaw)<br>獨立的入／出閘道（解決尾隨問題） | ❌ not implemented · 未實作 | see §19 · 見 §19 |
| Backup entry method when recognition fails (RFID, PIN, iAM Smart)<br>辨識失敗時的備用進入方式（RFID、密碼、iAM Smart） | ❌ not implemented · 未實作 | — |
| Administrator GUI<br>管理員圖形介面 | ❌ not implemented · 未實作 | — |

**English** — The project was validated against seven scripted test cases: unknown-user rejection, registered-user acceptance, deleting a non-existent name, camera network failure, occupancy calculation, room aggregation, and threshold filtering. All seven passed. The two honest failures — accuracy in poor lighting, and the tailgating toggle flaw — are documented in §19 rather than hidden.

**中文** — 專案以七個測試個案驗證：陌生人拒絕、已註冊住戶接受、刪除不存在的用戶、鏡頭網絡中斷、居住時數計算、單位彙總、門檻過濾。七項全部通過。至於兩個真實的不足 —— 光線不佳時辨識率下降、以及尾隨造成的切換錯亂 —— 都寫在 §19，而不是隱藏起來。

---

## 3. Architecture

**English** — The system is deliberately split into three tiers, because the three parts were developed in parallel by different team members and only had to agree on a handful of interfaces.

**中文** — 系統刻意分成三層，因為三部分由不同成員平行開發，彼此只需要就少數介面達成共識。

### 3.1 The three tiers · 三層架構

<p align="center">
  <img src="docs/images/architecture.png" alt="Overall architecture across the three tiers / 三層整體架構" width="100%">
</p>

**English**

- **Tier 1 — Hardware / IoT.** Two independent ESP32 boards. The **ESP32-S3-CAM** is nothing but a sensor: it connects to Wi-Fi and serves an MJPEG stream at `http://192.168.5.1:81/stream`. The second **ESP32** runs MicroPython and hosts a tiny web server: `GET /on` energises a relay, which opens the electromagnetic lock, and the firmware re-locks it automatically after a few seconds. Neither board runs any recognition logic — that keeps the firmware trivial and the heavy lifting on the PC.
- **Tier 2 — Python processing.** One folder of scripts on a laptop or mini-PC. `Control_System.py` is the only entry point an operator needs; it shells out to everything else. OpenCV does face detection (Haar Cascade), tracking (MOSSE) and recognition (LBPH). `requests` is used for exactly one thing: firing the HTTP unlock call.
- **Tier 3 — Data.** A single SQLite file, `database_pkpd.db`. No server, no credentials, no ORM. Two append-only event tables (`REC_ENTRY`, `REC_LEAVE`), one resident table (`Info`), and two families of generated report tables.

**中文**

- **第一層 — 硬件／物聯網。** 兩塊獨立的 ESP32 開發板。**ESP32-S3-CAM** 純粹是感測器：連上 Wi-Fi 後在 `http://192.168.5.1:81/stream` 提供 MJPEG 影像串流。第二塊 **ESP32** 跑 MicroPython，充當一個極簡網頁伺服器：收到 `GET /on` 就啟動繼電器，電磁鎖因而開啟，韌體會在數秒後自動重新上鎖。兩塊板都不執行任何辨識邏輯 —— 這樣韌體可以保持極簡，繁重運算全部留在電腦。
- **第二層 — Python 處理。** 一部筆電或迷你電腦上的一個資料夾。操作者只需要一個入口 `Control_System.py`，它會以子程序呼叫其他所有腳本。OpenCV 負責人臉偵測（Haar Cascade）、追蹤（MOSSE）與辨識（LBPH）。`requests` 只用在一件事上：發出解鎖的 HTTP 請求。
- **第三層 — 資料。** 單一 SQLite 檔案 `database_pkpd.db`。沒有伺服器、沒有帳密、沒有 ORM。兩張唯讀追加的事件表（`REC_ENTRY`、`REC_LEAVE`）、一張住戶表（`Info`），以及兩類自動產生的報表。

### 3.2 The two phases · 兩個階段

**English** — **Phase A — enrolment** happens once per resident, before they ever stand at the door. **Phase B — live recognition** runs continuously whenever the door is in use.

**中文** — **階段 A — 註冊**：每位住戶只需做一次，在他們真正站到門前之前完成。**階段 B — 即時辨識**：只要門在使用中就持續運行。

<p align="center">
  <img src="docs/images/registration-flow.png" alt="Enrolment and training sequence / 註冊與訓練時序" width="100%">
</p>

<p align="center">
  <img src="docs/images/runtime-sequence.png" alt="Live recognition, voting and unlock sequence / 即時辨識、投票與開鎖時序" width="100%">
</p>

**English** — The important design decision here is the **split between "detect", "track" and "recognise"**:

- The expensive Haar detection runs only every 10th frame. Running it on every frame would starve the video loop.
- Between detections, a cheap MOSSE tracker follows each known face's bounding box, so the same person keeps the same identity across frames.
- LBPH prediction runs on the tracked box. Recognition is a *distance*, not a probability: **lower is better**. Anything above `CONFIDENCE_THRESHOLD` (70) is treated as an unknown face.

Waiting for a single confident frame is not enough — a moment of good lighting could let a stranger through. So the recogniser keeps a per-face deque of success timestamps and only authorises once it has **10 successes inside a 4-second sliding window**, then clears the deque so the lock is not spammed while the person walks through. That is the anti-false-positive mechanism, and it is why the door does not flap open when somebody merely glances at the camera.

**中文** — 這裡最重要的設計決定，是把**「偵測」、「追蹤」與「辨識」拆開**：

- 成本最高的 Haar 偵測每 10 格才跑一次。若每格都跑，影像迴圈會被拖垮。
- 兩次偵測之間，用輕量的 MOSSE 追蹤器跟著每張已知人臉的邊界框，令同一個人在連續畫面中保持同一身分。
- LBPH 預測在追蹤框上執行。辨識結果是**距離**而非機率：**數值越小越像**。超過 `CONFIDENCE_THRESHOLD`（70）即視為陌生人。

只靠單一格的高信心並不足夠 —— 光線剛好的一剎那可能就讓陌生人通過。因此辨識器為每張臉維護一個成功時間戳佇列，必須在 **4 秒滑動視窗內累積 10 次成功**才授權開門，之後清空佇列，避免住戶還在穿門時不斷重複觸發。這就是防誤判機制，也是為甚麼有人只是望一望鏡頭時門不會亂開。

### 3.3 Entry vs. Leave: the "Single Door" toggle · 進與出：「單門」切換邏輯

**English** — The prototype has one camera for both directions, so the database has to infer direction from state. `sql_record.py` compares `Info.ENTRY_COUNT` with `Info.LEAVE_COUNT`.

**中文** — 原型只有一支鏡頭，兩個方向共用，因此資料庫必須從狀態推斷方向。`sql_record.py` 比較 `Info.ENTRY_COUNT` 與 `Info.LEAVE_COUNT`：

<p align="center">
  <img src="docs/images/entry-leave-toggle.png" alt="Entry vs Leave toggle state machine / 進出切換狀態機" width="100%">
</p>

**English** — This is elegant and needs no extra hardware, but it has a real flaw — tailgating — which is documented honestly in §19.

**中文** — 這個做法優雅、不需要額外硬件，但存在一個真實缺陷 —— 尾隨 —— 已在 §19 如實說明。

---

## 4. Bill of materials

**English** — Roughly HK$420–500 total. Prices are what the team paid in Hong Kong in late 2025 / early 2026; substitutes are fine.

**中文** — 總成本約 HK$420–500。價格為團隊於 2025 年底至 2026 年初在香港的實際支出；可自由選用替代品。

| # | Part · 零件 | Notes · 備註 | Approx. cost · 約價 |
|---|---|---|---|
| 1 | **ESP32-S3-CAM** board · 開發板 | The camera node. Any ESP32-CAM variant that can serve an MJPEG stream works; the URL path may differ.<br>鏡頭節點。任何能提供 MJPEG 串流的 ESP32-CAM 皆可，網址路徑可能不同。 | HK$80 |
| 2 | **ESP32** dev board (second unit) · 開發板（第二塊） | The relay node. Must be flashable with MicroPython (Thonny).<br>繼電器節點。需能以 MicroPython（Thonny）燒錄。 | HK$50 |
| 3 | **1-channel relay module**, 5 V coil, active-LOW · 單路繼電器模組 | Must have an opto-isolated input and COM/NO terminals.<br>需具光耦隔離輸入及 COM／NO 接點。 | HK$20 |
| 4 | **12 V electromagnetic lock** (fail-safe) · 12V 電磁鎖（斷電開門） | Fail-safe = unlocks when energised. 12 V DC supply.<br>Fail-safe 指通電即解鎖，使用 12V 直流。 | HK$150 |
| 5 | **12 V DC power supply** · 12V 電源供應器 | Sized for the lock's holding current (≈0.4 A typical).<br>需滿足鎖的維持電流（一般約 0.4 A）。 | HK$60 |
| 6 | **5 V supply / USB** for the ESP32 boards · 5V 電源 | Can be a phone charger plus USB cables.<br>手機充電器加 USB 線即可。 | HK$40 |
| 7 | **Breadboard + jumper wires** · 麵包板與杜邦線 | For the relay node and the power rails.<br>用於繼電器節點與電源軌。 | HK$30 |
| 8 | **Acrylic sheet, hinges, adhesive** · 亞克力板、鉸鏈、黏合劑 | The door prototype itself.<br>門的原型本體。 | HK$70 |
| 9 | *(recommended)* **flyback diode**, e.g. 1N4007 · （建議）飛輪二極管 | Across the lock coil. Cheap insurance against inductive spikes resetting the ESP32.<br>並接於鎖線圈，防止感應電壓尖峰令 ESP32 重置。 | HK$2 |
| 10 | *(recommended)* **multimeter** · （建議）萬用電錶 | For the power-rail diagnostics described in §5.3.<br>用於 §5.3 的電源軌量測。 | — |

> **Fail-safe vs fail-secure · 斷電開門與斷電鎖門**
>
> **English** — This build uses a *fail-safe* lock: cut the power and the door opens. That is the right choice for a prototype where a bug should not trap somebody, and the wrong choice for a real perimeter door. If you swap in a fail-secure strike, invert your expectations about power loss.
>
> **中文** — 本專案使用 *fail-safe*（斷電開門）電磁鎖：一旦斷電，門就會開啟。對原型而言這是正確選擇 —— 不該因為程式錯誤而把人困住；但對真實的保安門則是錯誤選擇。若改用 fail-secure（斷電鎖門）的電控鎖，請相應反轉你對斷電行為的預期。

---

## 5. Hardware assembly

### 5.1 Wiring · 接線

<p align="center">
  <img src="docs/images/hardware-wiring.png" alt="ESP32 to relay to electromagnetic lock wiring / ESP32 至繼電器至電磁鎖接線" width="100%">
</p>

**English** — The single most important thing in that diagram: **the PC talks to two different devices, and the devices never talk to each other.** The camera node streams video. The relay node accepts `GET /on`. If you accidentally point the door IP at the camera, nothing will happen and no useful error will appear.

Numbered connections:

1. **ESP32 (relay node) `GPIO26` → relay module `IN`.** Matches `RELAY_PIN = 26` in `ESP_RELAY.py`. Change both if you use another pin.
2. **ESP32 `5V` (or `VIN`) → relay `VCC`; ESP32 `GND` → relay `GND`.**
3. **Relay `COM` → 12 V supply positive.** **Relay `NO` (normally open) → lock positive terminal.**
4. **Lock negative terminal → 12 V supply negative.** The relay is only a switch in the positive leg; it does not supply power to the lock.
5. **Common ground.** The relay node's `GND`, the relay module's `GND` and the 12 V supply's negative rail must be tied together. Do **not** tie the 12 V positive rail to the 5 V logic rail.
6. **Flyback diode** across the lock coil, cathode to the positive terminal.

**中文** — 圖中最重要的一點：**電腦同時與兩個不同裝置通訊，而這兩個裝置彼此不溝通。** 鏡頭節點負責輸出影像，繼電器節點負責接收 `GET /on`。若你不小心把門的 IP 指向鏡頭，系統不會有任何反應，也不會出現有用的錯誤訊息。

逐條接線如下：

1. **ESP32（繼電器節點）`GPIO26` → 繼電器模組 `IN`。** 對應 `ESP_RELAY.py` 內的 `RELAY_PIN = 26`。若改用其他腳位，兩處都要改。
2. **ESP32 `5V`（或 `VIN`）→ 繼電器 `VCC`；ESP32 `GND` → 繼電器 `GND`。**
3. **繼電器 `COM` → 12V 電源正極。** **繼電器 `NO`（常開）→ 電磁鎖正極端子。**
4. **電磁鎖負極端子 → 12V 電源負極。** 繼電器只是正極迴路上的一個開關，本身不供電給鎖。
5. **共地。** 繼電器節點的 `GND`、繼電器模組的 `GND` 與 12V 電源的負極必須接在一起。**切勿**把 12V 正極接到 5V 邏輯電源軌。
6. **飛輪二極管** 並接於鎖線圈兩端，陰極接正極端子。

> **Powering the relay node from the same 5 V rail as the lock's supply is a common mistake.**
>
> **English** — The inrush when the lock energises can brown out the ESP32 and cause exactly the random Wi-Fi disconnects described in §17. Feed the boards from USB and the lock from its own 12 V brick.
>
> **中文** — 電磁鎖通電瞬間的湧浪電流會令 ESP32 電壓下陷，正好造成 §17 所述的隨機 Wi-Fi 斷線。請讓開發板由 USB 供電，鎖由獨立的 12V 電源供應器供電。

### 5.2 Reference build · 原型實物

<p align="center">
  <img src="docs/images/prototype-front.jpg" alt="The physical project: an acrylic door on a clear base plate with two hinges. An ESP32-S3-CAM is clipped to the top-left upright, a breadboard and ESP32 relay node sit along the top rail, and a 12 V electromagnetic lock is bolted to the inner face of the frame. / 專案本體：亞克力門裝在透明底板上，附兩隻鉸鏈。左上立柱夾著 ESP32-S3-CAM，頂部橫樑放著麵包板與 ESP32 繼電器節點，框架內側鎖上 12V 電磁鎖。" width="82%">
</p>

**English** — This is what the reader is building. Four things are visible in this one photograph, and they map directly onto the three tiers in §3:

| Visible in the photo · 圖中所見 | Tier · 層級 | Role · 作用 |
|---|---|---|
| **ESP32-S3-CAM** black board clipped to the top-left upright<br>夾在左上立柱的黑色 **ESP32-S3-CAM** | 1 — Hardware | The camera. Streams MJPEG over Wi-Fi; runs none of the recognition logic.<br>鏡頭。以 Wi-Fi 串流 MJPEG，不執行任何辨識邏輯。 |
| **Breadboard with the ESP32 relay node** along the top rail<br>頂部橫樑上的**麵包板與 ESP32 繼電器節點** | 1 — Hardware | The actuator controller. Hosts the web server that receives `GET /on`.<br>致動器控制器。運行接收 `GET /on` 的網頁伺服器。 |
| **12 V electromagnetic lock** bolted to the inner face, above the door panel<br>鎖在框架內側、門板上方的**12V 電磁鎖** | 1 — Hardware | The lock itself. Energised = open, auto re-locks after 5 s.<br>鎖體。通電即開，5 秒後自動重新上鎖。 |
| **Acrylic panel + two hinges** on a clear base plate<br>透明底板上的**亞克力門板與兩隻鉸鏈** | — | The scaled door that makes the demo openable and repeatable.<br>縮尺度門體，令示範可實際開合、可重複測試。 |

The PC that runs the Python recognition loop is **not** in the photograph — it sits off-camera, on the same Wi-Fi network, and is the only device that talks to both ESP32 boards.

**中文** — 這就是讀者要做出來的東西。單憑這一張照片就能看到四件事，而且它們直接對應 §3 的三層架構：

| Visible in the photo · 圖中所見 | Tier · 層級 | Role · 作用 |
|---|---|---|
| **ESP32-S3-CAM** 黑色板，夾在左上立柱<br>（同上） | 1 — 硬件 | 鏡頭。以 Wi-Fi 串流 MJPEG，不執行任何辨識邏輯。 |
| **麵包板 + ESP32 繼電器節點**，位於頂部橫樑<br>（同上） | 1 — 硬件 | 致動器控制器。運行接收 `GET /on` 的網頁伺服器。 |
| **12V 電磁鎖**，鎖在框架內側、門板上方<br>（同上） | 1 — 硬件 | 鎖體。通電即開，5 秒後自動重新上鎖。 |
| **亞克力門板 + 兩隻鉸鏈**，裝在透明底板<br>（同上） | — | 縮尺度門體，令示範可實際開合、可重複測試。 |

執行 Python 辨識迴圈的電腦**不在**照片中 —— 它位於鏡頭之外、同一個 Wi-Fi 網絡上，而且是唯一同時與兩塊 ESP32 通訊的裝置。

**English** — The team built a scaled acrylic door on a base plate with two hinges, sized so that the camera sees a face at roughly 50–100 cm and the lock's armature plate meets the frame squarely. In the photo above: the **ESP32-CAM clipped to the top-left upright**, the **breadboard and relay node along the top rail**, and the **electromagnetic lock bolted to the inner face of the frame**.

**中文** — 團隊以亞克力板製作了一個縮尺度的門，裝在底板並附兩隻鉸鏈，尺寸設計成鏡頭在約 50–100 公分距離看到人臉，而鎖的吸板能與門框平整貼合。上圖所見：**左上立柱夾著 ESP32-CAM**、**頂部橫樑放著麵包板與繼電器節點**，而**電磁鎖鎖在框架內側**。

### 5.3 Power-rail checks · 電源軌檢查

**English** — Before writing any firmware, measure:

- 5 V rail at the relay module under no load, then with the coil energised.
- 12 V rail at the lock terminals while unlocked.
- Continuity between every `GND` in the system.

If the 5 V rail sags below ~4.7 V when the relay clicks, fix the supply before touching the code.

**中文** — 在寫任何韌體之前，先量測：

- 繼電器模組的 5V 電源軌：空載時，以及線圈通電時。
- 解鎖狀態下，電磁鎖端子的 12V 電源軌。
- 系統內每一個 `GND` 之間的導通性。

若繼電器動作時 5V 電源軌跌至約 4.7V 以下，請先解決供電問題，之後才踫程式碼。
---

## 6. Flash the ESP32 boards

**English** — Both boards are programmed from the **Thonny IDE** over USB. Once flashed, the USB cable is only needed for power.

**中文** — 兩塊開發板都透過 USB、以 **Thonny IDE** 燒錄程式。燒錄完成後，USB 線只用作供電。

### 6.1 Camera node (ESP32-S3-CAM) · 鏡頭節點

**English** — Use the ESP32 camera example firmware that ships with your board's Arduino/ESP-IDF package, or any MJPEG camera sketch, and confirm you can open the stream in a browser:

**中文** — 使用你開發板 Arduino／ESP-IDF 套件附帶的 ESP32 鏡頭範例韌體，或任何 MJPEG 鏡頭 sketch，先確認能在瀏覽器開啟串流：

```
http://192.168.5.1:81/stream
```

**English** — The exact host and port depend entirely on your sketch and your router. Whatever URL works in the browser is the URL you put into `CAMERA_STREAM` in `public_variable.py`. Note that `cv2.VideoCapture()` can open MJPEG-over-HTTP directly, which is what this project relies on.

Set the camera node to a **fixed IP** — either a static lease in your router or a static IP in the sketch. Every point in this system is configured by IP, so a DHCP reassignment is a silent failure.

**中文** — 實際的主機與埠號完全取決於你的 sketch 與路由器設定。瀏覽器能開的那個網址，就是你要填進 `public_variable.py` 中 `CAMERA_STREAM` 的網址。注意 `cv2.VideoCapture()` 可以直接開啟 MJPEG-over-HTTP，本專案正是依賴這一點。

請為鏡頭節點設定**固定 IP** —— 在路由器做靜態指派，或在 sketch 內寫死。本系統每個環節都以 IP 設定，因此 DHCP 重新分配 IP 會造成「沒有任何錯誤訊息」的靜默失效。

### 6.2 Relay node (ESP32, MicroPython) · 繼電器節點

**English** — Step 1: install the MicroPython firmware on the board. Step 2: in Thonny, open `ESP_RELAY.py` from this repository and select **Run → Run current script**. Step 3: the console prints a small test menu.

**中文** — 第一步：為開發板安裝 MicroPython 韌體。第二步：在 Thonny 開啟本倉庫的 `ESP_RELAY.py`，選 **Run → Run current script**。第三步：主控台會顯示一個簡易測試選單。

```
Instruction: Type '1' to turn ON, '0' to turn OFF, or 'exit' to stop.
Enter Command: 1
>> [RELAY ON]
```

**English** — `1` energises the relay (lock opens), `0` releases it, `exit` releases it and stops the loop. **Verify the lock actually clicks here, before involving Python or OpenCV at all.** This one step eliminates the majority of "the door doesn't work" reports.

**中文** — 輸入 `1` 令繼電器通電（鎖開啟）、`0` 釋放、`exit` 釋放並結束迴圈。**請務必在還未涉及 Python 或 OpenCV 之前，先在此確認電磁鎖真的會「咔」一聲動作。** 這一步就能排除大部分「門不工作」的問題。

**English** — Step 4: once the relay is proven, replace the test loop with the web-server version below and save it as `main.py` on the board so it starts on boot.

**中文** — 第四步：繼電器驗證無誤後，把測試迴圈換成下面的網頁伺服器版本，並在板上存為 `main.py`，令開機時自動執行。

```python
# Sketch of the relay web server. Replace the GPIO pin and lock timing to suit
# your build, then save as main.py on the ESP32.
# 繼電器網頁伺服器範例。請按你的實作修改 GPIO 腳位與開鎖時間，
# 然後在 ESP32 上存為 main.py。
try:
    import usocket as socket
except ImportError:
    import socket
from machine import Pin
import time

RELAY_PIN = 26          # must match the wiring in section 5.1 / 必須與 5.1 節接線一致
UNLOCK_SECONDS = 5      # how long the lock stays open / 開鎖持續秒數

relay = Pin(RELAY_PIN, Pin.OUT)
relay.value(1)          # active-LOW module: 1 = relay released = locked
                        # 低電平觸發模組：1 = 繼電器釋放 = 上鎖


def unlock():
    relay.value(0)              # energise -> lock opens / 通電 -> 開鎖
    print(">> [RELAY ON] unlocked")
    time.sleep(UNLOCK_SECONDS)
    relay.value(1)              # de-energise -> lock closes / 斷電 -> 上鎖
    print(">> [RELAY OFF] locked")


# --- minimal HTTP server / 極簡 HTTP 伺服器 -----------------------------------
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("", 80))
s.listen(2)
print("Relay web server listening on port 80")

while True:
    conn, addr = s.accept()
    try:
        request = conn.recv(1024).decode()
        line = request.split("\r\n")[0]
        if "/on" in line:
            conn.send("HTTP/1.1 200 OK\r\n\r\nUNLOCKED")
            conn.close()
            unlock()
        elif "/off" in line:
            conn.send("HTTP/1.1 200 OK\r\n\r\nLOCKED")
            conn.close()
            relay.value(1)
        else:
            conn.send("HTTP/1.1 404 Not Found\r\n\r\n")
            conn.close()
    except Exception as e:
        print("request error:", e)
        conn.close()
```

**English** — Step 5: test from the PC, on the same Wi-Fi network.

**中文** — 第五步：在同一 Wi-Fi 網絡的電腦上測試。

```bash
curl http://192.168.5.2/on        # the lock should click open for 5 s
                                  # 電磁鎖應「咔」一聲開啟 5 秒
```

**English** — `192.168.5.2` is the relay node's address in this build. `track_and_recognize.py` has it hard-coded as `DOOR_ESP_IP` — change it there, or better, move it into `public_variable.py` as described in §16.

**中文** — `192.168.5.2` 是本專案中繼電器節點的位址。`track_and_recognize.py` 把它寫死為 `DOOR_ESP_IP` —— 請在該處修改，或更好是按照 §16 所述把它移到 `public_variable.py` 統一管理。

> **Blocking is fine here. · 這裡用阻塞式寫法沒有問題**
>
> **English** — `time.sleep(5)` inside the request handler means the board serves one unlock at a time. For a single door with one resident walking through, that is adequate and much easier to debug than an interrupt-driven design.
>
> **中文** — 在請求處理函式中 `time.sleep(5)`，代表開發板一次只能處理一次開鎖。對單一門口、一次一位住戶通過的情境而言，這已經足夠，而且比中斷驅動的設計容易除錯得多。

---

## 7. Software setup

**English** — Windows is the primary target (the project's automation uses Windows Task Scheduler); macOS and Linux notes are called out where they differ.

**中文** — 主要以 Windows 為目標（本專案的自動化排程使用 Windows 工作排程器）；macOS 與 Linux 的差異會另行標示。

### 7.1 Python and the OpenCV build that has `cv2.face` · 必須安裝含 `cv2.face` 的 OpenCV

**English** — **This is the step people get wrong.** Plain `opencv-python` does **not** include the `cv2.face` module, and `process_and_train.py` calls `cv2.face.LBPHFaceRecognizer_create()`. You need the **contrib** package.

**中文** — **這是最多人出錯的一步。** 普通的 `opencv-python` **不包含** `cv2.face` 模組，而 `process_and_train.py` 會呼叫 `cv2.face.LBPHFaceRecognizer_create()`。你必須安裝 **contrib** 版本。

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

`requirements.txt`:

```
opencv-contrib-python>=4.8.0
numpy>=1.24
requests>=2.31
python-dateutil>=2.8.2
```

```bash
pip install -r requirements.txt
```

**English** — Verify before going further.

**中文** — 繼續之前先驗證。

```bash
python -c "import cv2; print(cv2.__version__); print(cv2.face.LBPHFaceRecognizer_create())"
```

**English** — If that raises `AttributeError: module 'cv2' has no attribute 'face'`, you have the wrong OpenCV wheel. Uninstall and reinstall:

**中文** — 若出現 `AttributeError: module 'cv2' has no attribute 'face'`，代表你裝錯了 OpenCV 套件。請解除安裝後重裝：

```bash
pip uninstall opencv-python opencv-contrib-python -y
pip install opencv-contrib-python
```

> **macOS note · macOS 備註**
>
> **English** — Apple Silicon wheels for `opencv-contrib-python` are available and work. If the webcam preview fails, grant Terminal (or your IDE) camera permission under *System Settings → Privacy & Security → Camera*. In `public_variable.py`, use `CAM_INDEX = 0` for a built-in webcam or `1` for many USB cameras.
>
> **中文** — `opencv-contrib-python` 已有 Apple Silicon 版本的 wheel，可正常使用。若鏡頭預覽失敗，請在 *系統設定 → 私隱與安全性 → 相機* 中授權 Terminal（或你的 IDE）使用鏡頭。在 `public_variable.py` 中，內建鏡頭用 `CAM_INDEX = 0`，多數 USB 鏡頭用 `1`。

> **Linux note · Linux 備註**
>
> **English** — Install the windowing and video backends first: `sudo apt install libgl1 libglib2.0-0 v4l-utils`. Check the camera index with `v4l2-ctl --list-devices`.
>
> **中文** — 先安裝視窗與影像後端：`sudo apt install libgl1 libglib2.0-0 v4l-utils`。以 `v4l2-ctl --list-devices` 查看鏡頭編號。

### 7.2 Thonny

**English** — Thonny is only needed for the ESP32 work in §6. Install it from [thonny.org](https://thonny.org) and confirm it can see your board over USB.

**中文** — Thonny 只在 §6 的 ESP32 工作中需要。請從 [thonny.org](https://thonny.org) 安裝，並確認它能透過 USB 看到你的開發板。

### 7.3 Network · 網絡

**English** — All three devices — PC, camera node, relay node — must be on the **same LAN**, and the boards must be on **2.4 GHz Wi-Fi** (most ESP32 variants cannot join 5 GHz networks). Write down the two IP addresses; you will need them in the next step.

**中文** — 三部裝置 —— 電腦、鏡頭節點、繼電器節點 —— 必須在同一個**區域網絡**，而兩塊開發板必須連上 **2.4 GHz Wi-Fi**（大部分 ESP32 型號無法連接 5 GHz 網絡）。請記下兩個 IP 位址，下一步會用到。

---

## 8. Configure `public_variable.py`

**English** — Every path, IP and threshold lives in one file. This is deliberately the **first file you edit**, so that no other script needs touching when you move the project or change networks.

**中文** — 所有路徑、IP 與門檻值都集中在同一個檔案。這是刻意設計成**你要改的第一個檔案**，這樣當你搬動專案或更換網絡時，不需要碰任何其他腳本。

```python
# public_variable.py

BASE_DIR = Path(__file__).resolve().parent   # the folder this file lives in
                                              # 本檔案所在的資料夾（無需修改）

IMAGES_DIR    = BASE_DIR / "Images"            # raw captures, created on first run
                                               # 原始擷取影像，首次執行時自動建立
PROCESSED_DIR = BASE_DIR / "Images_processed"  # grayscale 200x200 crops / 灰階 200x200 裁切
MODEL_PATH    = BASE_DIR / "model.yml"         # trained LBPH model / 已訓練 LBPH 模型
LABELS_PATH   = BASE_DIR / "labels.json"       # {"name": id} / 姓名對應編號

ESP32_URL  = "http://192.168.5.1:81/stream"    # camera node / 鏡頭節點
CAM_INDEX  = ESP32_URL                         # or 0 for a local webcam / 或 0 使用本機鏡頭
DOOR_ESP_IP = "192.168.5.2"                    # relay node / 繼電器節點

IMG_SIZE = (200, 200)
CASCADE  = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

RECOG_INTERVAL_FRAMES = 10   # run detection every N frames / 每 N 格執行一次偵測
CONFIDENCE_THRESHOLD  = 70   # LBPH distance; LOWER is a better match / 距離越小越像
WINDOW_TIME           = 1.0  # seconds of the voting window / 投票視窗秒數
REQUIRED_COUNT        = 10   # successes needed inside that window / 視窗內需成功次數

FunFileL = [ ... ]           # absolute paths used by Control_System.py
                             # Control_System.py 使用的絕對路徑清單
```

**English** — Checklist — **you only need step 1 and 2**:

1. **`BASE_DIR`** — already handled. It resolves to the folder containing `public_variable.py`, so a fresh clone works with no editing at all. If you want the face data on another drive or share, replace it with an explicit path and use forward slashes even on Windows, which avoids the classic `\U` escape problem in Python strings.
2. **`ESP32_URL`** — the address that showed video in your browser in §6.1.
3. **`DOOR_ESP_IP`** — the relay node's address, the one `curl` reached in §6.2. `track_and_recognize.py` imports this value, so there is one place to change.
4. **`FunFileL`** — no editing needed either. It is derived from `BASE_DIR`, and `Control_System.py` indexes it by menu position.

**中文** — 檢查清單 —— **只需處理第 1 及第 2 項**：

1. **`BASE_DIR`** —— 已經處理好。它會指向 `public_variable.py` 所在的資料夾，所以全新 clone 後完全無需修改。若想把人臉資料放到其他硬碟或網絡磁碟，請改成明確路徑；即使在 Windows 也請用正斜線 `/`，可避開 Python 字串中經典的 `\U` 轉義問題。
2. **`ESP32_URL`** —— §6.1 中瀏覽器能顯示影像的那個網址。
3. **`DOOR_ESP_IP`** —— 繼電器節點的位址，即 §6.2 中 `curl` 能成功連上的那個。`track_and_recognize.py` 會匯入這個值，所以只需改一處。
4. **`FunFileL`** —— 同樣無需修改。它由 `BASE_DIR` 推算，`Control_System.py` 依選單編號索引它。

> **A note on the two threshold constants. · 關於兩組門檻常數的說明**
>
> **English** — `public_variable.py` and `track_and_recognize.py` both declare `CONFIDENCE_THRESHOLD`, `REQUIRED_COUNT` and `WINDOW_TIME`, and they are kept at the **same values** on purpose. This is a historical artefact of two developers building in parallel: the recognition loop sets its own constants rather than importing them, so a change must be made in both files. If the door never unlocks, a mismatch between these two sets of numbers is the first thing to check.
>
> The network addresses, by contrast, have been consolidated: `track_and_recognize.py` imports `DOOR_ESP_IP` and `ESP32_URL` from `public_variable.py`, so changing a board's IP means editing exactly one line.
>
> **中文** — `public_variable.py` 與 `track_and_recognize.py` 都各自宣告了 `CONFIDENCE_THRESHOLD`、`REQUIRED_COUNT` 與 `WINDOW_TIME`，並且刻意**保持相同數值**。這是兩位開發者平行開發留下的歷史痕跡：辨識迴圈用自己的常數而非匯入，所以改動必須同時在兩個檔案進行。如果門永遠不開，首先要檢查的就是這兩組數字是否一致。
>
> 相對地，網絡位址已經統一：`track_and_recognize.py` 從 `public_variable.py` 匯入 `DOOR_ESP_IP` 與 `ESP32_URL`，所以更換開發板 IP 只需改一行。

---

## 9. Initialise the database

**English** — Create the SQLite file and its three base tables.

**中文** — 建立 SQLite 檔案及其三張基礎表。

```bash
python database_init.py
```

**English** — Expected output:

**中文** — 預期輸出：

```
database 'database_pkpd.db' has been built successfully.
```

**English** — This creates:

**中文** — 這會建立：

| Table · 表 | Purpose · 用途 |
|---|---|
| `Info` | One row per resident: ID, name, room, running entry/leave counts, `living` flag.<br>每位住戶一列：編號、姓名、房間、累計進出次數、`living` 標記。 |
| `REC_ENTRY` | Append-only log of arrivals.<br>只追加的進入記錄。 |
| `REC_LEAVE` | Append-only log of departures.<br>只追加的離開記錄。 |

**English** — The monthly report tables (`Mon_YYYY`, `Mon_YYYY_ROOM`) are **not** created here — `compare.py` and `room_time.py` build them on demand.

**中文** — 每月報表（`Mon_YYYY`、`Mon_YYYY_ROOM`）**不會**在這裡建立 —— 由 `compare.py` 與 `room_time.py` 按需要產生。

**English** — Verify with any SQLite browser, or from the command line.

**中文** — 可用任何 SQLite 瀏覽器，或在命令列驗證：

```bash
python -c "import sqlite3; print(sqlite3.connect('database_pkpd.db').execute(\"SELECT name FROM sqlite_master WHERE type='table'\").fetchall())"
```

> **Resetting · 重置**
>
> **English** — To start from a clean slate, delete `database_pkpd.db`, empty `Images/`, `Images_processed/`, delete `model.yml` and reset `labels.json` to `{}`, then re-run `database_init.py`. Never delete the database without also clearing the face data — you will end up with a trained model that recognises people the database has never heard of.
>
> **中文** — 想由零開始：刪除 `database_pkpd.db`、清空 `Images/` 與 `Images_processed/`、刪除 `model.yml`、把 `labels.json` 重設為 `{}`，然後重新執行 `database_init.py`。切勿只刪資料庫而保留人臉資料 —— 那樣你會得到一個「認得人、但資料庫沒有這個人」的模型。

---

## 10. First run

**English** — Everything is driven from one menu.

**中文** — 所有操作都由同一個選單驅動。

```bash
python Control_System.py
```

```
Functions List
1. Scan your face for registration.
2. Train the model (You must finish 1 first!).
3. Scan your face to enter.
4. Delete user information.
5. Update user information.
6. Generate residents' report.
7. Generate rooms' report.
8. Find the issue rooms
Type 'END' or 'end' to stop the program.
Please choose the action:
```

**English** — A complete smoke test, in order:

**中文** — 完整的功能測試，按以下次序進行：

| Step · 步驟 | Menu · 選單 | Do this · 操作 | Expect · 預期結果 |
|---|---|---|---|
| 1 | `1` | Enter a name, then a room, then face the camera<br>輸入姓名、房間，然後面向鏡頭 | A window with a blue box; it counts up to 30 captures; `Images/<name>_<timestamp>_<i>.jpg` files appear.<br>出現視窗並畫藍框，計數至 30，產生 `Images/` 下的影像檔。 |
| 2 | `2` | — | `Images_processed/*.png` appear, `labels.json` gets an entry, `model.yml` is written.<br>產生處理後影像、`labels.json` 新增項目、寫出 `model.yml`。 |
| 3 | `3` | Stand in front of the camera<br>站在鏡頭前 | A green box labelled `<name> (n)`; after 10 hits the relay clicks and a row lands in `REC_ENTRY`.<br>出現綠色框標示 `<name> (n)`，累積 10 次後繼電器動作，`REC_ENTRY` 新增一列。 |
| 4 | `3` | Step away, then come back<br>離開後再回來 | A row lands in `REC_LEAVE` instead.<br>改為在 `REC_LEAVE` 新增一列。 |
| 5 | `6` | Answer `Y` to "last month"<br>回答 `Y` 選上個月 | Per-resident hours printed and stored in `Mon_YYYY`.<br>顯示每人時數並存入 `Mon_YYYY`。 |
| 6 | `7` | — | Per-room totals stored in `Mon_YYYY_ROOM`.<br>每戶總時數存入 `Mon_YYYY_ROOM`。 |
| 7 | `8` | — | Rooms under 150 hours listed.<br>列出低於 150 小時的單位。 |

<details>
<summary><strong>Worked example: what the terminal output looks like · 實際終端輸出示例</strong></summary>

```
Functions List
1. Scan your face for registration.
...
Please choose the action: 8

Valid input.

Would you like to check the report of last month? (Y/N): N
Would you like to check the report of other month? (Y/N): Y
Enter the year you want to check: 2026
Enter the month you want to check in integer: 4

--- Apr_2026 less than 150hr ---
Room | Total Time
-------------------------------------------------------
A1011    | 61.43
A1101    | 14.98
A1234    | 9.15
-------------------------------------------------------
```

</details>

> **Option 5 ("Update user information") is a macro, not a distinct feature. · 選項 5 是一個巨集，而非獨立功能**
>
> **English** — It runs delete → capture → retrain in sequence, which is exactly the right workflow when a resident's appearance changes (new glasses, shaved head) or when their first capture set was poor. It is also the slowest option, because it retrains the whole model.
>
> **中文** — 它依序執行「刪除 → 重新擷取 → 重新訓練」，正是住戶外觀改變（換眼鏡、剃光頭）或首次擷取品質不佳時應採用的流程。它同時也是最慢的選項，因為要重新訓練整個模型。
---

## 11. Daily operation

**English** — Once a resident is enrolled, day-to-day life is just menu option `3` running in the background.

**中文** — 住戶完成註冊後，日常運作就只是在背景執行選單選項 `3`。

```bash
python track_and_recognize.py
```

**English** — Press `q` in the video window to stop.

**中文** — 在影像視窗按 `q` 結束。

<p align="center">
  <img src="docs/images/terminal-session.png" alt="Terminal showing the menu, the camera stream URL, repeated unlock attempts and graceful failure messages / 終端畫面：選單、鏡頭串流網址、重複的解鎖嘗試與優雅失敗訊息" width="92%">
</p>

**English** — *Above: a real session from the project's test phase. Menu option `3` starts the recognition loop, which connects to the camera stream immediately. The `Read timed out` lines are the PC trying to reach the relay node on `192.168.5.2` while it was powered down — the important detail is that the video loop **kept running and reported the failure** instead of crashing. That is the non-fatal error handling working as designed.*

**中文** — *上圖：專案測試階段的真實終端畫面。選單選項 `3` 啟動辨識迴圈，並立即連接鏡頭串流。那些 `Read timed out` 是電腦嘗試連上位於 `192.168.5.2` 的繼電器節點，而該節點當時未通電 —— 關鍵在於影像迴圈**繼續運作並回報失敗**，而不是崩潰。這正是非致命錯誤處理按設計運作。*

**English** — What happens on a successful recognition, in order:

1. LBPH returns a label and a distance. Distance ≥ 70 → the box is labelled `Unknown` and nothing else happens.
2. Distance < 70 → the timestamp is pushed into that tracked face's deque.
3. Deque length ≥ 10 within the window → the lock is triggered and the deque is cleared.
4. `sql_input_select(name)` decides Entry or Leave and writes the row.

**中文** — 一次成功辨識的完整流程：

1. LBPH 回傳標籤與距離。距離 ≥ 70 → 框標示為 `Unknown`，其餘不作任何動作。
2. 距離 < 70 → 把當前時間戳推入該張臉的佇列。
3. 視窗內佇列長度 ≥ 10 → 觸發開鎖，並清空佇列。
4. `sql_input_select(name)` 判斷是進入或離開，並寫入資料列。

**English** — Two operational notes:

- **Recognition runs on the tracked bounding box, not on a fresh detection.** If somebody is tracked badly (a hand in front of the face, a fast turn), the box drifts and confidence degrades. Losing the track and being re-detected is often better than holding a bad track; the shipped code drops a tracker after 30 unseen frames.
- **Stopping the script mid-session is safe.** Nothing is cached in memory: every unlock writes its own database row immediately.

**中文** — 兩點運作須知：

- **辨識是在追蹤框上執行，而不是每次重新偵測。** 若某人被追蹤得很差（手擋住臉、快速轉頭），框會漂移，信心值隨之下降。失去追蹤再被重新偵測，往往比硬保留一個壞追蹤框更好；倉庫中的程式碼會在 30 格未再見到目標後丟棄該追蹤器。
- **中途停止腳本是安全的。** 記憶體中沒有暫存狀態：每次開鎖都立即寫入自己的資料列。

---

## 12. The monthly reporting cycle

<p align="center">
  <img src="docs/images/monthly-lifecycle.png" alt="Monthly lifecycle: reset, accumulate, compare, aggregate, flag / 每月週期：重置、累積、計算、彙總、標示" width="100%">
</p>

**English** — Run the reports in this order — each one consumes the previous one's output.

**中文** — 請按此順序執行報表 —— 每一步都消費上一步的產出。

```bash
python compare.py       # menu 6 — hours per resident  -> Mon_YYYY
                        # 選單 6 — 每人時數 -> Mon_YYYY
python room_time.py     # menu 7 — hours per room      -> Mon_YYYY_ROOM
                        # 選單 7 — 每戶時數 -> Mon_YYYY_ROOM
python check_report.py  # menu 8 — rooms under 150 h
                        # 選單 8 — 低於 150 小時的單位
```

**English** — Each script is interactive: it offers *last month* or a month you type in. Both `compare.py` and `room_time.py` **drop and rebuild** their output table on every run, so re-running them is always safe and never double-counts.

**中文** — 每個腳本都是互動式：可選「上個月」，或自行輸入指定年月。`compare.py` 與 `room_time.py` 每次執行都會**先刪除再重建**輸出表，因此重複執行永遠安全，也不會重複計算。

**English** — **How the hours are actually computed.** `compare.py` fetches the resident's `REC_ENTRY` and `REC_LEAVE` rows for the target month, subtracts each entry time from the corresponding leave time, and sums the deltas:

**中文** — **時數實際上是怎樣算出來的。** `compare.py` 取出該住戶在目標月份的 `REC_ENTRY` 與 `REC_LEAVE` 記錄，把每次的離開時間減去對應的進入時間，然後把差值加總：

```
total_hours = Σ (LEAVE_TIME − ENTRY_TIME) / 3600
```

**English** — This is a positional pairing — the *n*-th entry is matched with the *n*-th leave. It is simple, fast, and correct as long as the toggle state never gets out of sync. Tailgating (see §19) is precisely the situation that breaks that assumption.

**中文** — 這是**按位置配對** —— 第 *n* 筆進入配第 *n* 筆離開。做法簡單、快速，而且只要切換狀態從不錯亂就是正確的。尾隨（見 §19）正是破壞這個假設的情況。

**English** — **The 150-hour threshold** lives in `check_report.py`:

**中文** — **150 小時門檻**位於 `check_report.py`：

```python
query = f"SELECT ROOM, TOTAL_TIME FROM {target_month}_ROOM WHERE Total_Time < 150"
```

**English** — Change that constant to match your own policy before you generate a report you intend to act on.

**中文** — 在你產生任何打算據以行動的報表之前，請先把這個常數改成本身政策所定的數值。

### Under-occupancy report output · 低於門檻的報表輸出

<p align="center">
  <img src="docs/images/report-output.png" alt="Terminal output from check_report.py listing rooms below 150 hours / check_report.py 列出低於 150 小時單位的終端輸出" width="58%">
</p>

**English** — *Above: the output of menu option `8` during the threshold test. Three rooms are flagged below the 150-hour line. After one room's figure was manually raised to 151 hours, it correctly disappeared from the list.*

**中文** — *上圖：門檻測試期間選單選項 `8` 的輸出。三個單位被標示為低於 150 小時。把其中一個單位的時數手動改為 151 小時後，它正確地從名單中消失。*

---

## 13. Automate the monthly reset

**English** — `reset.py` handles the awkward case: a resident who is *inside* the building when the calendar month changes. Without it, their entry would be paired with a leave in the following month and their hours would be wrong at both ends.

**中文** — `reset.py` 處理一個棘手情況：住戶在曆月交替時**仍在單位內**。若沒有它，該次進入會與下個月的離開配對，兩邊的時數都會算錯。

**English** — The logic, per resident:

**中文** — 每位住戶的處理邏輯：

| State at rollover · 交替時的狀態 | What `reset.py` does · `reset.py` 的動作 |
|---|---|
| `ENTRY_COUNT > LEAVE_COUNT` (inside)<br>（在單位內） | Writes a synthetic leave at 23:59 on the last day of the old month, a synthetic entry at 00:00 on the first day of the new month, then sets `ENTRY_COUNT = 1, LEAVE_COUNT = 0`.<br>在舊月最後一日 23:59 補一筆「離開」，在新月第一日 00:00 補一筆「進入」，然後設 `ENTRY_COUNT = 1, LEAVE_COUNT = 0`。 |
| `ENTRY_COUNT <= LEAVE_COUNT` (outside)<br>（不在單位內） | Sets both counters to `0`. No synthetic rows.<br>把兩個計數歸零，不補任何記錄。 |

### Windows (Task Scheduler) · Windows（工作排程器）

**English** — The repository ships `monthly_db_reset.xml`, a ready-made task definition that runs on the 1st of every month.

**中文** — 倉庫附有 `monthly_db_reset.xml`，是現成的工作定義，於每月 1 日執行。

1. **English:** Press <kbd>Win</kbd>+<kbd>R</kbd>, type `taskschd.msc`, press Enter. **中文：** 按 <kbd>Win</kbd>+<kbd>R</kbd>，輸入 `taskschd.msc`，按 Enter。
2. **English:** In the right-hand **Actions** pane, click **Import Task…** **中文：** 在右側 **Actions（動作）** 窗格點選 **Import Task…（匯入工作）**。
3. **English:** Select `monthly_db_reset.xml` from this folder. **中文：** 選擇本資料夾中的 `monthly_db_reset.xml`。
4. **English:** Open the **Actions** tab, select the imported action, click **Edit**, and replace both absolute paths with your own. **中文：** 切到 **Actions** 分頁，選取匯入的動作並按 **Edit**，把兩個絕對路徑改成你自己的：
   - **English:** the program: `C:\path\to\your\venv\Scripts\python.exe` **中文：** 程式：`C:\path\to\your\venv\Scripts\python.exe`
   - **English:** the argument: `C:\path\to\Living-Hour-Counting-System-ESP32\reset.py` **中文：** 引數：`C:\path\to\Living-Hour-Counting-System-ESP32\reset.py`
   - **English:** and set **Start in** to the project folder, so the script finds `database_pkpd.db`. **中文：** 並把 **Start in（起始位置）** 設為專案資料夾，令腳本找得到 `database_pkpd.db`。
5. **English:** Click **OK**, then right-click the task and choose **Run** to test it once immediately. **中文：** 按 **OK**，然後在該工作上按右鍵選 **Run** 立即測試一次。

### macOS and Linux (cron) · macOS 與 Linux（cron）

**English** — Add one line with `crontab -e`:

**中文** — 用 `crontab -e` 加入一行：

```cron
0 0 1 * * cd /path/to/Living-Hour-Counting-System-ESP32 && /path/to/venv/bin/python reset.py >> reset.log 2>&1
```

**English** — That runs at 00:00 on the 1st of every month. **Schedule the reset to happen earlier than any report you generate**, and check `reset.log` after the first run.

**中文** — 這會在每月 1 日 00:00 執行。**請把重置排在你產生任何報表之前**，並在首次執行後檢查 `reset.log`。

> **Run the reset before the reports, not after. · 重置要在報表之前，而非之後**
>
> **English** — `compare.py` pairs entries with leaves; if the rollover has not happened yet, the resident who stayed overnight will have an unmatched entry and their total will be short by a whole month.
>
> **中文** — `compare.py` 會把進入與離開配對；若尚未執行跨月結轉，那位跨月留宿的住戶就會有一筆沒有對應的進入記錄，其總時數會少算整整一個月。

---

## 14. Repository map

<p align="center">
  <img src="docs/images/file-map.png" alt="Repository map grouped by responsibility / 按職責分組的檔案地圖" width="100%">
</p>

```
Living-Hour-Counting-System-ESP32/
├── Control_System.py         # entry point: the 1-8 menu / 入口：1-8 選單
├── public_variable.py        # all paths, IPs and thresholds / 所有路徑、IP、門檻
├── capture.py                # register a resident's face / 註冊住戶人臉
├── process_and_train.py      # preprocess + train the LBPH model / 前處理並訓練
├── track_and_recognize.py    # live detect / track / recognise / unlock / 即時辨識與開鎖
├── delete_user.py            # purge a resident / 徹底刪除住戶
├── database_init.py          # create the SQLite schema / 建立資料庫結構
├── sql_record.py             # register residents; Entry/Leave toggle; logging / 記錄進出
├── compare.py                # hours per resident per month / 每人每月時數
├── room_time.py              # hours per flat per month / 每戶每月時數
├── check_report.py           # flag flats below 150 hours / 標示低於 150 小時
├── reset.py                  # month-end rollover / 月結結轉
├── door_trigger.py           # standalone voting helper (not imported) / 獨立投票輔助類別
├── monthly_db_reset.xml      # Windows Task Scheduler definition / 工作排程器定義
├── ESP_RELAY.py              # MicroPython firmware for the relay node / 繼電器節點韌體
├── requirements.txt
├── .gitignore
├── Images/                   # (git-ignored) raw captures / 原始影像（已忽略）
├── Images_processed/         # (git-ignored) grayscale crops / 灰階裁切（已忽略）
├── model.yml                 # (git-ignored) trained model / 已訓練模型（已忽略）
├── labels.json               # (git-ignored) name -> id map / 姓名對應表（已忽略）
├── docs/images/              # diagrams used by this README / 本文件的圖表
└── legacy/
    └── sql_record_in.py      # early data-layer prototype (superseded) / 早期資料層原型
```

> **One naming trap. · 一個命名陷阱**
>
> **English** — `public_variable.py` still carries a `FunFileL` list of hard-coded absolute paths from the machine the project was developed on (`C:/Users/kaila/...`). It is also where the *current* scripts are supposed to be listed. Until you edit it, `Control_System.py` will fail to launch anything. Everything else in the tree above is referenced by relative path and needs no change.
>
> An earlier draft of the data layer lives in **`legacy/sql_record_in.py`**. It called `sql_input(...)` at import time and used different column names (`RECORD_ENTRY`, `ENTRY_COUNT`). It is superseded by `sql_record.py` and is kept only so the project's history stays traceable. It is in its own folder precisely so that nobody imports it by accident — **do not import it, and do not run it.** If you want a genuine starting point for the data layer, read `database_init.py` and `sql_record.py`.
>
> **中文** — `public_variable.py` 仍保留一份 `FunFileL` 清單，內含開發機器上的寫死絕對路徑（`C:/Users/kaila/...`）。這裡同時也是**現行**腳本應該被列出的地方。在你修改它之前，`Control_System.py` 將無法啟動任何東西。上表其他檔案都以相對路徑引用，無需修改。
>
> 資料層的早期草稿放在 **`legacy/sql_record_in.py`**。它在 import 時就呼叫 `sql_input(...)`，而且使用不同的欄位名稱（`RECORD_ENTRY`、`ENTRY_COUNT`）。它已被 `sql_record.py` 取代，保留只為讓專案歷史可追溯。特意放進獨立資料夾，就是為了避免有人誤 import —— **請勿 import，也請勿執行。** 若你想要一個真正可用的資料層起點，請讀 `database_init.py` 與 `sql_record.py`。

### What is *not* in this repository, and why · 本倉庫沒有包含甚麼，以及原因

| Missing · 缺少 | Why · 原因 | How to get it · 如何取得 |
|---|---|---|
| `Images/`, `Images_processed/` | They contain real people's faces.<br>內含真人人臉影像。 | Created by `capture.py` when you enrol your own residents.<br>註冊你自己的住戶時由 `capture.py` 產生。 |
| `model.yml` | A trained biometric model is personal data.<br>已訓練的生物特徵模型屬個人資料。 | Created by `process_and_train.py`.<br>由 `process_and_train.py` 產生。 |
| `labels.json` | Same — it maps names to model labels.<br>同理，它把姓名對應到模型標籤。 | Created by `process_and_train.py`.<br>由 `process_and_train.py` 產生。 |
| `database_pkpd.db` | Contains residents' names, rooms and movement history.<br>含住戶姓名、房間與出入紀錄。 | Created by `database_init.py`; it starts empty.<br>由 `database_init.py` 產生，初始為空。 |
| The relay web server firmware<br>繼電器網頁伺服器韌體 | Only the bench-test version (`ESP_RELAY.py`) is included.<br>只包含測試版 `ESP_RELAY.py`。 | §6.2 contains a working web-server script to drop in.<br>§6.2 提供可直接使用的網頁伺服器程式碼。 |
| `ESP32-CAM` camera sketch<br>鏡頭 sketch | Board-specific.<br>依開發板而異。 | Use any MJPEG example for your board; see §6.1.<br>使用你開發板的任何 MJPEG 範例，見 §6.1。 |

**English** — The **enrolment and reporting workflows cannot be demonstrated on a fresh clone until you create the first four items yourself** — that is intentional, and it is the privacy design described in §18.

**中文** — **在全新 clone 的狀態下，必須先自行建立上表前四項，才能示範註冊與報表流程** —— 這是刻意的，正是 §18 所述的私隱設計。

### How the modules depend on each other · 模組之間的依賴關係

| Module · 模組 | Imports / calls · 匯入／呼叫 | Called by · 被誰呼叫 |
|---|---|---|
| `Control_System.py` | `public_variable`, `sql_record`; `subprocess` | the operator · 操作者 |
| `capture.py` | `public_variable` | `Control_System.py` |
| `process_and_train.py` | `public_variable` | `Control_System.py`, `delete_user.py` |
| `track_and_recognize.py` | `sql_record`; `requests` | `Control_System.py` |
| `delete_user.py` | `public_variable`; `subprocess` | `Control_System.py` |
| `sql_record.py` | `sqlite3` | `track_and_recognize.py`, `Control_System.py` |
| `compare.py` / `room_time.py` | `table_exists` from `compare.py` | `Control_System.py` |
| `check_report.py` | `compare.table_exists` | `Control_System.py` |
| `reset.py` | `sqlite3`, `dateutil` | Windows Task Scheduler / cron |
| `ESP_RELAY.py` | `machine` (MicroPython) | the ESP32 itself — it never runs on the PC<br>ESP32 本身 —— 不會在電腦上執行 |
| `legacy/sql_record_in.py` | *(nothing)* — standalone draft<br>*（無）* —— 獨立草稿 | nobody. Superseded by `sql_record.py`; kept for provenance only.<br>沒有。已被 `sql_record.py` 取代，僅作歷史留存。 |

**English** — Six of the scripts (`compare.py`, `room_time.py`, `check_report.py`, `reset.py`, `database_init.py`, `sql_record.py`) run perfectly well standalone — each has a `__main__` block with its own prompts. `Control_System.py` is a convenience layer over them, not a requirement.

**中文** — 其中六個腳本（`compare.py`、`room_time.py`、`check_report.py`、`reset.py`、`database_init.py`、`sql_record.py`）完全可以獨立執行 —— 各自都有帶互動提示的 `__main__` 區塊。`Control_System.py` 只是它們之上的便利層，並非必要。

**English** — `door_trigger.py` defines a `DoorControl` class that implements the same 10-in-4-seconds voting rule with a console simulator instead of the real relay call. Nothing imports it — it is the logic experiment that the inline voting code in `track_and_recognize.py` grew out of, and it is useful as a reference if you want the voting rule isolated from the OpenCV loop.

**中文** — `door_trigger.py` 定義了一個 `DoorControl` 類別，以主機台模擬器（而非真實繼電器呼叫）實作同一套「4 秒內 10 次」的投票規則。沒有任何檔案 import 它 —— 它是 `track_and_recognize.py` 內嵌投票程式碼的前身實驗，若你想把投票規則從 OpenCV 迴圈中抽離出來，它是有用的參考。
---

## 15. Database schema

<p align="center">
  <img src="docs/images/database-erd.png" alt="SQLite entity relationship diagram / SQLite 實體關係圖" width="100%">
</p>

### `Info` — one row per resident · 每位住戶一列

| Column · 欄位 | Type · 型別 | Notes · 說明 |
|---|---|---|
| `RES_ID` | TEXT | Primary key. Generated as `<ROOM><NN>`, e.g. the third person in room `A101` is `A10103`.<br>主鍵。格式為 `<房間><序號>`，例如 A101 房的第三位住戶是 `A10103`。 |
| `RES_NAME` | TEXT | Must match the name used in filenames and `labels.json`.<br>必須與檔名及 `labels.json` 中的姓名一致。 |
| `RES_ROOM` | TEXT | Flat identifier used for room-level aggregation.<br>單位識別碼，用於每戶彙總。 |
| `ENTRY_COUNT` | INTEGER | Running total of entries. Half of the toggle state.<br>累計進入次數，切換狀態的一半。 |
| `LEAVE_COUNT` | INTEGER | Running total of leaves. The other half.<br>累計離開次數，切換狀態的另一半。 |
| `living` | INTEGER | `1` = currently enrolled, `0` = moved out. Reports filter on `living = 1`.<br>`1` = 在住，`0` = 已遷出。報表只取 `living = 1`。 |

### `REC_ENTRY` and `REC_LEAVE` — the audit trail · 稽核軌跡

| Column · 欄位 | Notes · 說明 |
|---|---|
| `RES_ID` | FK-by-convention to `Info`.<br>慣例上的外鍵，指向 `Info`。 |
| `REC_Number` | Human-readable event ID: `RES_ID_YEAR_MONTH_COUNT`, e.g. `A10103_2026_Apr_17`.<br>可讀的事件編號，例如 `A10103_2026_Apr_17`。 |
| `ENTRY_TIME` / `LEAVE_TIME` | `YYYY-MM-DD HH:MM`. **Note the format is minutes-precision, no seconds** — `compare.py` parses it with `"%Y-%m-%d %H:%M"`. Changing it breaks the report.<br>格式為 `YYYY-MM-DD HH:MM`。**注意只到分鐘、沒有秒** —— `compare.py` 以 `"%Y-%m-%d %H:%M"` 解析，改動格式會令報表失效。 |
| `YEAR_E` / `YEAR_L` | 4-digit year string, used for filtering.<br>四位年份字串，用於篩選。 |
| `MOUTH_E` / `MOUTH_L` | Month abbreviation (`Jan`, `Feb`, …). The misspelling is inherited from the original schema and appears in the queries; do not "fix" it in one place only.<br>月份縮寫（`Jan`、`Feb`…）。這個拼寫錯誤沿自原始結構並出現在查詢中；切勿只在一處「修正」它。 |

### Generated report tables · 自動產生的報表

| Table · 表 | Created by · 產生者 | Contents · 內容 |
|---|---|---|
| `Mon_YYYY` (e.g. `Mar_2026`) | `compare.py` | `RES_ID`, `RES_NAME`, `RES_ROOM`, `Total_Time` (hours, 2 dp).<br>每人時數（小時，兩位小數）。 |
| `Mon_YYYY_ROOM` | `room_time.py` | `ROOM`, `TOTAL_TIME` — `Total_Time` summed per room.<br>每戶時數，按房間加總。 |

**English** — Both are rebuilt from scratch on every run, so they are disposable. The `REC_*` tables are the source of truth.

**中文** — 兩者每次執行都重新建立，因此可隨時丟棄。`REC_*` 兩張表才是資料的唯一真實來源。

> **No foreign keys are declared. · 沒有宣告任何外鍵**
>
> **English** — SQLite will happily let you insert a `REC_ENTRY` row for a `RES_ID` that does not exist in `Info`. The Python layer is the only thing maintaining referential integrity — worth remembering if you ever write to the database by hand.
>
> **中文** — 即使 `Info` 中不存在該 `RES_ID`，SQLite 仍會接受你插入一筆 `REC_ENTRY`。維護參照完整性的只有 Python 層 —— 若你日後手動寫入資料庫，請記住這一點。

---

## 16. Configuration reference

**English** — Everything tunable, in one place.

**中文** — 所有可調參數，集中一處。

| Setting · 設定 | File · 檔案 | Default · 預設 | Meaning · 含義 |
|---|---|---|---|
| `BASE_DIR` | `public_variable.py` | *(auto)*<br>自動 | Resolves to the folder containing `public_variable.py`; only override it to store face data elsewhere.<br>自動指向 `public_variable.py` 所在資料夾；只有想把人臉資料存到別處時才需覆寫。 |
| `ESP32_URL` | `public_variable.py` | `http://192.168.5.1:81/stream` | Camera node stream.<br>鏡頭節點串流。 |
| `CAM_INDEX` | `public_variable.py` | `ESP32_URL` | Use `0` / `1` for a local USB webcam instead.<br>改成本機 USB 鏡頭時用 `0`／`1`。 |
| `DOOR_ESP_IP` | `public_variable.py` | `192.168.5.2` | Relay node address, imported by the recognition loop.<br>繼電器節點位址，由辨識迴圈匯入。 |
| `IMG_SIZE` | `public_variable.py` | `(200, 200)` | ROI size fed to LBPH. Must match between training and recognition.<br>餵給 LBPH 的區域尺寸，訓練與辨識必須一致。 |
| `RECOG_INTERVAL_FRAMES` | `public_variable.py` | `10` | Detection cadence in the live loop. Lower = more CPU.<br>即時迴圈的偵測間隔，數值越小越耗 CPU。 |
| `CONFIDENCE_THRESHOLD` | both · 兩處 | `50` | Maximum LBPH distance still considered a match. **Lower = stricter.**<br>仍視為同一人的最大 LBPH 距離。**數值越小越嚴格。** |
| `REQUIRED_COUNT` | both · 兩處 | `10` | Successful recognitions required before unlocking.<br>開鎖前所需的成功辨識次數。 |
| `WINDOW_TIME` | both · 兩處 | `4.0` | Length of the voting window in seconds.<br>投票視窗長度（秒）。 |
| `delay_between` | `capture.py` | `0.2` | Seconds between captures during enrolment.<br>註冊時每次擷取的間隔秒數。 |
| `num_images` | `capture.py` | `30` | Images captured per resident.<br>每位住戶擷取的影像數。 |
| `150` | `check_report.py` | `150` | Monthly occupancy threshold in hours.<br>每月居住時數門檻（小時）。 |
| `RELAY_PIN` | `ESP_RELAY.py` | `26` | GPIO driving the relay.<br>驅動繼電器的 GPIO。 |
| `UNLOCK_SECONDS` | relay firmware · 繼電器韌體 | `5` | How long the lock stays open.<br>開鎖持續時間。 |

**English** — **Tuning guidance.** If the door unlocks for the wrong person, lower `CONFIDENCE_THRESHOLD`. If it never unlocks for the right person, raise it, lengthen `WINDOW_TIME`, or decrease `RECOG_INTERVAL_FRAMES` so recognition runs on more frames. Change one value at a time and note what you changed — the LBPH distance is not comparable between models, because retraining renumbers the labels.

**中文** — **調校建議。** 如果門為錯誤的人開啟，請降低 `CONFIDENCE_THRESHOLD`。如果正確的人永遠開不了門，請提高它、延長 `WINDOW_TIME`，或把 `RECOG_INTERVAL_FRAMES` 調小讓辨識跑在更多畫格上。每次只改一個值並記錄改了甚麼 —— LBPH 距離在不同模型之間不可比較，因為重新訓練會重新編號標籤。

---

## 17. Troubleshooting

### `AttributeError: module 'cv2' has no attribute 'face'`

**English** — You installed `opencv-python` instead of `opencv-contrib-python`. See §7.1.

**中文** — 你安裝了 `opencv-python` 而非 `opencv-contrib-python`。見 §7.1。

### `RuntimeError: Cannot turn on the camera`

**English** — The stream URL is wrong or unreachable. Open `http://192.168.5.1:81/stream` in a browser **on the same Wi-Fi network**. If the browser fails, the problem is the camera node, not Python. Check that the PC is on 2.4 GHz and that the camera has a fixed IP.

**中文** — 串流網址錯誤或無法連線。請**在同一個 Wi-Fi 網絡**的瀏覽器開啟 `http://192.168.5.1:81/stream`。若瀏覽器也失敗，問題在鏡頭節點，而非 Python。請確認電腦連的是 2.4 GHz，且鏡頭已有固定 IP。

### The video window opens but no faces are ever detected · 影像視窗開了但從未偵測到人臉

**English** — Either the face is too small (the cascade needs at least 80×80 pixels — move closer, or lower `minSize`), the lighting is too flat, or the camera is aimed too high or too low. Steps 1 and 2 of the smoke test should be done in the same lighting as the real door.

**中文** — 可能人臉太小（cascade 至少需要 80×80 像素 —— 靠近一點，或把 `minSize` 調小）、光線太平淡，或鏡頭角度過高／過低。功能測試的第 1、2 步應在與真實門口相同的光線條件下進行。

### Recognition labels everyone `Unknown` · 所有人都被判為 Unknown

**English** — `CONFIDENCE_THRESHOLD` is too strict for your camera and lighting, or `model.yml` is stale. Re-run option `2` after adding a resident, and try a threshold of 80–90 to see whether recognition works at all, then tighten it.

**中文** — `CONFIDENCE_THRESHOLD` 對你的鏡頭與光線而言過於嚴格，或 `model.yml` 已過期。新增住戶後請重跑選項 `2`；先把門檻放寬到 80–90 看辨識是否根本可行，然後再收緊。

### `[Error] unsuccessful connecting ESP32: ... Read timed out`

**English** — The camera works, the relay node does not. Ping it from the PC (`ping 192.168.5.2`), confirm `curl http://192.168.5.2/on` clicks the relay, and confirm the Thonny script is still running or saved as `main.py`. This error is non-fatal by design — recognition keeps running.

**中文** — 鏡頭正常，但繼電器節點有問題。從電腦 ping 它（`ping 192.168.5.2`）、確認 `curl http://192.168.5.2/on` 會令繼電器動作，並確認 Thonny 腳本仍在執行或已存為 `main.py`。這個錯誤按設計是非致命的 —— 辨識會繼續運作。

### ESP32 keeps dropping off Wi-Fi, or reboots when the lock fires · ESP32 不斷斷線，或開鎖時重啟

**English** — Almost always a power problem. Feed the boards from USB and the lock from its own 12 V supply, add the flyback diode, and check the 5 V rail with a multimeter under load (§5.3).

**中文** — 幾乎總是供電問題。請讓開發板由 USB 供電、鎖由獨立 12V 電源供電，加裝飛輪二極管，並在負載下用萬用電錶量測 5V 電源軌（§5.3）。

### The door opens but no row appears in the database · 門開了但資料庫沒有新增記錄

**English** — `sql_record.py` or the database file is not where the script expects. The connection is opened by relative filename (`sqlite3.connect('database_pkpd.db')`), so **the scripts must be run from the project folder**. When launching from a scheduler or an IDE, set the working directory explicitly.

**中文** — `sql_record.py` 或資料庫檔案不在腳本預期的位置。連線是以相對檔名開啟（`sqlite3.connect('database_pkpd.db')`），因此**必須在專案資料夾內執行腳本**。從排程器或 IDE 啟動時，請明確設定工作目錄。

### `labels.json 或 model.yml not exist` / `model.yml or labels.json are not found`

**English** — Enrolment was never trained. Run menu option `2`, or `python process_and_train.py`.

**中文** — 註冊後從未訓練。請執行選單選項 `2`，或 `python process_and_train.py`。

### The report shows 0.0 hours for somebody who was definitely there · 明明在家的住戶報表顯示 0.0 小時

**English** — Their `REC_ENTRY` and `REC_LEAVE` rows are not paired — usually because the toggle state is inverted (tailgating), or because the month they were logged in does not match the month you are reporting, or because `reset.py` has not run yet for the month boundary. Query `REC_ENTRY` and `REC_LEAVE` directly for that `RES_ID` and look at the raw timestamps.

**中文** — 他們的 `REC_ENTRY` 與 `REC_LEAVE` 沒有正確配對 —— 通常是切換狀態被反轉（尾隨）、記錄所屬月份與你查詢的月份不符，或跨月時尚未執行 `reset.py`。請直接查詢該 `RES_ID` 的 `REC_ENTRY` 與 `REC_LEAVE`，檢視原始時間戳。

### `compare.py` reports `IndexError` or pairs the wrong times · `compare.py` 出現 IndexError 或配對錯誤

**English** — `LT[i] - ET[i]` is positional. If a resident has more entries than leaves in the target month (or vice versa), the counts do not line up. Check for a missing leave, which is what the rollover in `reset.py` exists to prevent.

**中文** — `LT[i] - ET[i]` 是按位置配對。若某住戶在目標月份內的進入筆數多於離開（或相反），數量就對不上。請檢查是否缺少一筆離開記錄 —— 這正是 `reset.py` 的跨月結轉要預防的情況。

---

## 18. Privacy and data handling

**English** — This system processes **biometric data**, which is among the most sensitive categories of personal data under Hong Kong's Personal Data (Privacy) Ordinance (PDPO) and comparable laws elsewhere. A working prototype is not a lawful deployment.

Consequently, this repository **ships no face images and no trained model**:

- `Images/`, `Images_processed/`, `model.yml`, `labels.json` and `database_pkpd.db` are git-ignored. You create them locally when you enrol your own face.
- Never commit a real resident's photographs, name, room number, or entry/exit history to a public repository.

**中文** — 本系統處理**生物特徵資料**，這在香港《個人資料（私隱）條例》（PDPO）及各地同類法例下，屬於最敏感的個人資料類別之一。一個能運作的原型，並不等於一個合法的部署。

因此，本倉庫**不包含任何人臉影像，也不包含已訓練的模型**：

- `Images/`、`Images_processed/`、`model.yml`、`labels.json` 與 `database_pkpd.db` 都已被 git 忽略。它們會在你註冊自己的人臉時於本機產生。
- 切勿把真實住戶的相片、姓名、房間號或進出紀錄提交到公開倉庫。

**English** — If you build on this project, treat the following as minimum requirements, not options:

1. **Consent and notice.** Residents must know what is captured, why, who sees the reports, and how long records are kept. The project's stated purpose — supportive follow-up, not punishment — has to be communicated to the people being monitored, or the system becomes surveillance.
2. **Purpose limitation.** Use the occupancy data only for the stated occupancy question. Do not repurpose the logs for disciplinary or unrelated purposes.
3. **Retention limit.** `delete_user.py` exists so that a departed resident's data can be purged completely. Run it when somebody moves out, and define a retention period for `REC_*` logs.
4. **Access control.** `database_pkpd.db` is an unencrypted file with no authentication. Anyone with file access can read every entry and exit. In any real deployment, encrypt the volume and restrict access to the reporting operator.
5. **Data minimisation.** Store what the policy question needs. A monthly hour total and the raw events that produce it are defensible; keeping full-resolution video indefinitely is not.

**中文** — 若你要在此專案上繼續開發，請把以下各點視為最低要求，而非選項：

1. **同意與告知。** 住戶必須知道系統擷取甚麼、為何擷取、誰會看到報表，以及紀錄保存多久。專案聲明的目的 —— 支援性跟進而非懲罰 —— 必須向被監測者清楚傳達，否則系統就變成監控。
2. **目的限制。** 居住時數資料只能用於所述的居住時數問題，不得轉用於紀律處分或無關用途。
3. **保存期限。** `delete_user.py` 的存在，就是為了能徹底清除已遷出住戶的資料。有人遷出時請執行它，並為 `REC_*` 紀錄訂立保存期限。
4. **存取控制。** `database_pkpd.db` 是無加密、無認證的檔案，任何能讀取該檔案的人都能看到所有進出紀錄。在任何真實部署中，請加密儲存媒體並限制只有報表操作者可存取。
5. **資料最小化。** 只儲存政策問題所需的資料。每月總時數及產生它的原始事件是合理的；無限期保留全解析度影像則不然。

**English** — The team's own stated position is in the project report: the goal is to help ensure public housing reaches the people who need it, and to route anomalies to **social workers for supportive intervention** rather than to penalties.

**中文** — 團隊本身在專案報告中的立場是：目標是協助確保公屋資源分配給真正有需要的人，並把異常個案轉介給**社工提供支援性介入**，而非施加懲罰。

---

## 19. Known limitations and roadmap

**English** — These are the honest failures of the prototype, not excuses.

**中文** — 以下是原型真實的不足，而非藉口。

| Limitation · 限制 | Why it happens · 成因 | What to do about it · 改善方向 |
|---|---|---|
| **Tailgating inverts the toggle state.** A resident who follows somebody else through without being scanned has their Entry/Leave polarity permanently reversed, corrupting their hours.<br>**尾隨會令切換狀態反轉。** 住戶跟在他人身後通過而未被掃描，其進出極性會永久反轉，時數因而出錯。 | One camera serves both directions; direction is inferred from counters rather than measured.<br>一支鏡頭服務兩個方向，方向是由計數推斷而非實際量測。 | Separate physical IN and OUT terminals, an interior exit button, or a turnstile. Any of those removes the toggle entirely.<br>設置獨立的入／出閘道、室內出門按鈕，或改用旋轉閘。任一方案都能完全取消切換邏輯。 |
| **Poor accuracy in bad lighting or at unusual angles.**<br>**光線不佳或角度異常時準確度下降。** | LBPH on 200×200 grayscale crops from a low-cost camera is the cheapest viable pipeline, and it is not robust to illumination or pose.<br>以低成本鏡頭取得 200×200 灰階裁切再跑 LBPH，是最便宜可行的流程，對光照與姿態並不穩健。 | Preprocess harder (histogram equalisation, CLAHE), tune LBPH grid/radius/neighbours, add capture guidance at enrolment, or move to an embedding model on a small edge accelerator.<br>加強前處理（直方圖均衡、CLAHE）、調整 LBPH 的 grid／radius／neighbours、在註冊時加入取像指引，或改用小型邊緣加速器上的嵌入模型。 |
| **No liveness detection.** A high-resolution photograph or a phone screen can fool the camera.<br>**沒有活體偵測。** 高解析度相片或手機屏幕可欺騙鏡頭。 | Not implemented — the pipeline has no depth, IR or motion-cue check.<br>未實作 —— 流程中沒有深度、紅外或動作線索的檢查。 | Add an IR/depth camera, or a challenge-response cue (blink, turn head) before authorising.<br>加入紅外／深度鏡頭，或在授權前加入挑戰回應提示（眨眼、轉頭）。 |
| **No backup entry method.** If recognition fails, an authorised resident cannot get in.<br>**沒有備用進入方式。** 辨識失敗時，合法住戶也進不了門。 | Out of scope for the semester.<br>超出本學期範圍。 | Combine with RFID or a PIN as a second factor, or issue QR codes via iAM Smart.<br>加入 RFID 或密碼作為第二因素，或經 iAM Smart 發出二維碼。 |
| **Command-line only.** Housing staff would have to use a terminal.<br>**只有命令列介面。** 房屋署職員必須使用終端機。 | Built for demonstration.<br>為示範而建。 | A small web dashboard over the same SQLite file — the data model does not need to change.<br>以同一個 SQLite 檔案為基礎做一個小型網頁儀表板 —— 資料模型無需改動。 |
| **Config is inconsistent between files.** `WINDOW_TIME` and `CONFIDENCE_THRESHOLD` are declared in two places with different values.<br>**設定檔之間不一致。** `WINDOW_TIME` 與 `CONFIDENCE_THRESHOLD` 在兩處宣告且數值不同。 | Rapid parallel development.<br>平行快速開發所致。 | Single source of truth in `public_variable.py`; make every script import from it.<br>以 `public_variable.py` 為唯一真實來源，令每個腳本都從它匯入。 |
| **Single-PC, single-door.** No concurrency handling beyond SQLite's own locking.<br>**單機、單門。** 除了 SQLite 自身的鎖定機制外，沒有並行處理。 | Prototype scope.<br>原型範圍。 | A server-side database with one writer per door, or an event queue.<br>改用伺服器端資料庫，每道門一個寫入者，或引入事件佇列。 |

**English** — An honest summary: the concept is proven end-to-end, the security design (tracking plus multi-frame voting) works, and the administrative reporting works. The parts that would need real engineering before deployment are **liveness detection**, **eliminating the single-door toggle**, and **lighting robustness**.

**中文** — 誠實的總結：概念已端到端驗證，保安設計（追蹤加多影格投票）有效，行政報表亦能運作。真正需要工程投入才能部署的部分是**活體偵測**、**取消單門切換邏輯**，以及**光線穩健性**。
---

## 20. Team and credits

**English** — Project: **Public Housing Entrance Monitoring System / Living Hour Counting System** — HKU SPACE Community College, Associate of Engineering, CCIT4080 *Project on Knowledge Product Development*, Group CL11-01, Semester 2. Supervisor: **Dr Yu Wai Ming**.

**中文** — 專案：**公共房屋出入監測系統／居住時數統計系統** —— HKU SPACE 社區書院工程學副學士，CCIT4080「知識產品開發專案」，組別 CL11-01，第二學期。指導老師：**余偉明博士**。

| Member · 成員 | Contribution · 貢獻 |
|---|---|
| **Wong Chun Cheung (Alex)** | **Project leader & lead developer.** Designed the OpenCV pipeline end to end: `capture.py`, `process_and_train.py`, and `track_and_recognize.py` including the MOSSE tracker and the multi-frame voting mechanism. Built the hardware–software integration: turned the ESP32 into a local web server and wired the `requests` unlock call into the recognition loop. Consolidated the scripts into `Control_System.py` and led testing and debugging.<br>**專案組長及主要開發者。** 端到端設計 OpenCV 流程：`capture.py`、`process_and_train.py`，以及含 MOSSE 追蹤器與多影格投票機制的 `track_and_recognize.py`。完成軟硬件整合：把 ESP32 變成區域網頁伺服器，並將 `requests` 解鎖呼叫接入辨識迴圈。把各腳本整合為 `Control_System.py`，並主導測試與除錯。 |
| **Wong Kailas** | **Database architecture & data management layer.** Designed and implemented the SQLite schema — the separation of static metadata (`Info`) from dynamic temporal logs (`REC_*` and the monthly report tables) — and engineered the reporting/aggregation logic in `sql_record.py`, `compare.py`, `room_time.py`, `check_report.py` and `reset.py`, including the `GROUP BY`/`SUM` aggregation and the Entry/Leave toggle algorithm. Contributed the control-system and delete/update utilities built on Alex's foundation, with parameterised queries and cross-platform validation.<br>**資料庫架構與資料管理層。** 設計並實作 SQLite 結構 —— 把靜態元資料（`Info`）與動態時序紀錄（`REC_*` 及每月報表）分離 —— 並開發 `sql_record.py`、`compare.py`、`room_time.py`、`check_report.py`、`reset.py` 的報表與彙總邏輯，包括 `GROUP BY`／`SUM` 彙總及進出切換演算法。在 Alex 的基礎上完成控制系統與刪除／更新工具，使用參數化查詢並進行跨平台驗證。 |
| **Lau Cheung Ching (Alec)** | Hardware development lifecycle: procurement (ESP32, ESP32-CAM, relay module, electromagnetic lock), physical construction on the acrylic board, breadboard and cabling, and the Thonny-based ESP32 firmware for the lock handshake.<br>硬件開發週期：採購（ESP32、ESP32-CAM、繼電器模組、電磁鎖）、亞克力板上的實體組裝、麵包板與配線，以及以 Thonny 開發的 ESP32 開鎖交握韌體。 |
| **Lin Cheuk Hin (Hin)** | Hardware assembly and the door prototype: sourcing the acrylic sheet, hinges and adhesive, and the final mechanical design (dimensions, hinge placement, component mounting).<br>硬件組裝與門的原型：採購亞克力板、鉸鏈與黏合劑，以及最終機械設計（尺寸、鉸鏈位置、元件安裝）。 |
| **Chow Tsun Hung (Johnny)** | Hardware integration and physical prototyping: translating schematics into a stabilised breadboard assembly, power-rail diagnostics with a multimeter, and the motor-driven door mechanism.<br>硬件整合與實體原型：把電路圖落實為穩定的麵包板組裝、以萬用電錶進行電源軌診斷，以及馬達驅動的門機構。 |

### Attribution of the database layer · 資料庫層的貢獻歸屬

**English** — The repository's database layer — `database_init.py`, `sql_record.py`, `compare.py`, `room_time.py`, `check_report.py` and `reset.py` — is **Kailas Wong's work**. Together these modules define the schema, maintain referential integrity by convention, implement the Entry/Leave toggle, and produce the monthly resident- and room-level occupancy reports that give the project its purpose. The recognition pipeline feeds this layer through the single `sql_input_select(name)` call; everything downstream of that call is his design.

**中文** — 本倉庫的資料庫層 —— `database_init.py`、`sql_record.py`、`compare.py`、`room_time.py`、`check_report.py` 與 `reset.py` —— 是 **Kailas Wong 的作品**。這些模組共同定義資料結構、以慣例維護參照完整性、實作進出切換，並產生賦予本專案意義的每月每人及每戶居住時數報表。辨識流程只透過單一 `sql_input_select(name)` 呼叫接入這一層；該呼叫下游的一切都是他的設計。

### Dependencies and prior art · 依賴與前人研究

**English** — This project stands on well-established open-source and academic work:

- **OpenCV** — Haar Cascade detection, MOSSE tracking, and the LBPH face recogniser.
- **LBPH** — Ahonen, Hadid & Pietikäinen (2006), *Face description with local binary patterns*.
- **Eigenfaces / Fisherfaces** — Turk & Pentland (1991); Belhumeur, Hespanha & Kriegman (1997), evaluated and set aside as too sensitive to lighting and pose.
- **Deep embedding models** — DeepFace (Taigman et al., 2014), FaceNet (Schroff et al., 2015), ArcFace (Deng et al., 2019). Rejected here on compute and dataset grounds, not on accuracy.
- **Comparable work** — Choudhary et al. (2025) demonstrated the ESP32-CAM + OpenCV access-control pattern that this project extends from a door lock into occupancy auditing.

**中文** — 本專案建基於成熟的開源及學術成果之上：

- **OpenCV** —— Haar Cascade 偵測、MOSSE 追蹤與 LBPH 人臉辨識器。
- **LBPH** —— Ahonen、Hadid 與 Pietikäinen（2006），*Face description with local binary patterns*。
- **Eigenfaces／Fisherfaces** —— Turk 與 Pentland（1991）；Belhumeur、Hespanha 與 Kriegman（1997）；經評估後因對光照與姿態過於敏感而未採用。
- **深度嵌入模型** —— DeepFace（Taigman 等，2014）、FaceNet（Schroff 等，2015）、ArcFace（Deng 等，2019）。此處因運算資源與資料集限制而未採用，並非因其準確度不足。
- **同類研究** —— Choudhary 等（2025）示範了 ESP32-CAM 加 OpenCV 的門禁模式，本專案把它由門鎖延伸至居住時數稽核。

**English** — The full reference list is in the project report.

**中文** — 完整參考文獻請見專案報告。

### Building on this project · 在此專案上繼續開發

**English** — If you use this design, please credit the team and keep the non-punitive framing. If you fix the toggle flaw or add liveness detection, a pull request describing what you changed and how you tested it would be genuinely welcome — those are the two changes that would move this from a prototype to something deployable.

**中文** — 若你採用這個設計，請註明團隊並保留「非懲罰性」的定位。如果你修正了切換邏輯的缺陷，或加入了活體偵測，非常歡迎提交 pull request 並說明你改了甚麼、如何測試 —— 這兩項改動正是把原型推進到可部署階段的關鍵。

---

## Appendix: verifying the reports by hand

**English** — When a report number looks wrong, go to the source. Open an interactive session in the project folder.

**中文** — 當報表數字看起來不對，直接查回源頭。在專案資料夾開啟互動式 Python：

```bash
python
```

```python
import sqlite3
con = sqlite3.connect("database_pkpd.db")
c = con.cursor()

room = input("Room: ")
res = input("Resident name: ")
year, month = input("Year: "), input("Month (Jan/Feb/...): ")

# who is enrolled in that room right now? / 該房間目前登記了誰？
c.execute("SELECT RES_ID, RES_NAME, ENTRY_COUNT, LEAVE_COUNT, living "
          "FROM Info WHERE RES_ROOM = ? AND RES_NAME = ?", (room, res))
for row in c.fetchall():
    print("Info      :", row)

# every entry and leave that the report is based on / 報表依據的每一筆進出
c.execute("SELECT ENTRY_TIME, REC_Number FROM REC_ENTRY "
          "WHERE YEAR_E = ? AND MOUTH_E = ? ORDER BY ENTRY_TIME", (year, month))
print("entries   :", c.fetchall())
c.execute("SELECT LEAVE_TIME, REC_Number FROM REC_LEAVE "
          "WHERE YEAR_L = ? AND MOUTH_L = ? ORDER BY LEAVE_TIME", (year, month))
print("leaves    :", c.fetchall())

# the total the report should be producing / 報表應該算出的總數
hour_entries = c.execute("SELECT ENTRY_TIME FROM REC_ENTRY WHERE YEAR_E = ? AND MOUTH_E = ?",
                         (year, month)).fetchall()
hour_leaves = c.execute("SELECT LEAVE_TIME FROM REC_LEAVE WHERE YEAR_L = ? AND MOUTH_L = ?",
                        (year, month)).fetchall()
from datetime import datetime
fmt = "%Y-%m-%d %H:%M"
total = sum((datetime.strptime(l[0], fmt) - datetime.strptime(e[0], fmt)).total_seconds() / 3600
            for e, l in zip(hour_entries, hour_leaves))
print("total     :", round(total, 2), "hours")

con.close()
```

**English** — If the hand-computed total differs from `Mon_YYYY`, the entry/leave lists are not the same length — and that is the toggle flaw, showing up in your data.

**中文** — 若你手算的總數與 `Mon_YYYY` 不符，代表進入與離開的清單長度不同 —— 那就是切換邏輯的缺陷，出現在你的資料之中。
