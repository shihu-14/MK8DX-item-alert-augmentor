# YOLOv8 + OpenCVによるリアルタイム顔判定付き物体検出（範囲限定・確信度評価あり）

import cv2
import numpy as np
import time
from ultralytics import YOLO

# YOLO学習済みモデルの読み込み
model = YOLO("runs/detect/train/weights/best.pt")

# 顔検出用のHaar Cascadeモデルの読み込み（高速）
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# 表示用画像（例：Piranha-Plant.png）
display_img = cv2.imread("assets/icons/alerts/Piranha-Plant.png")
if display_img is None:
    raise RuntimeError("表示する画像（icon.png）が読み込めません")

# キャプチャ開始
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise IOError("キャプチャデバイスが開けません")

ret, frame = cap.read()
if not ret:
    raise RuntimeError("カメラからフレームが取得できません")

h, w = frame.shape[:2]
fps = 30
CONF_THRESHOLD = 0.7
FACE_CONF_THRESHOLD = 0  # 顔の大きさに基づく簡易的な確信度指標（Haarは信頼度を返さないため面積で代用）

# 除外赤枠の座標
display_active = False
display_start_time = 0
display_pos = (0, 0)
display_scale = 1.0

center_x, center_y = w // 2, h // 2 + 230
box_width, box_height = 400, 380
ex_x1 = center_x - box_width // 2
ex_y1 = center_y - box_height // 2
ex_x2 = center_x + box_width // 2
ex_y2 = center_y + box_width // 2
slice_h = h // 5

while True:
    ret, frame = cap.read()
    if not ret:
        print("フレーム取得失敗")
        break

    annotated_frame = frame.copy()
    now = time.time()

    # 顔検出（検出範囲：赤枠内）
    roi_gray = cv2.cvtColor(frame[ex_y1:ex_y2, ex_x1:ex_x2], cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(
    roi_gray,
    scaleFactor=1.05,
    minNeighbors=3,
    minSize=(20, 20)
)

    # faces = face_cascade.detectMultiScale(roi_gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    # 顔が検出された場合のみ推論（顔の面積を信頼度の代替とする）
    face_in_area = False
    for (fx, fy, fw, fh) in faces:
        area = fw * fh
        if area >= FACE_CONF_THRESHOLD:
            face_in_area = True
            break

    boxes = []
    if face_in_area:
        # 除外領域以外をマスク
        mask = np.ones((h, w), dtype=np.uint8) * 255
        mask[0:slice_h, :] = 0
        mask[h-slice_h:h, :] = 0
        mask[ex_y1:ex_y2, ex_x1:ex_x2] = 0
        masked_frame = cv2.bitwise_and(frame, frame, mask=mask)

        # YOLO推論
        results = model(masked_frame)
        boxes = results[0].boxes

    # 検出結果を描画
    for box in boxes:
        if box.conf >= CONF_THRESHOLD:
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            cls_id = int(box.cls)
            conf = float(box.conf)
            cv2.rectangle(annotated_frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
            label = f"{results[0].names[cls_id]} {conf:.2f}"
            cv2.putText(annotated_frame, label, (int(x1), int(y1) - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # 面積 → 表示サイズスケーリング
            area = (x2 - x1) * (y2 - y1)
            scale = min(max(0.2, 20000 / (area + 1)), 2.0)

            center_x_box = (x1 + x2) / 2
            flipped_x = w - int(center_x_box)
            img_h, img_w = display_img.shape[:2]
            resized_w = int(img_w * scale)
            resized_h = int(img_h * scale)
            display_pos = (max(0, min(w - resized_w, flipped_x - resized_w // 2)), h - resized_h - 10)
            display_scale = scale
            display_start_time = now
            display_active = True

    # 赤線で除外領域を描画
    cv2.rectangle(annotated_frame, (ex_x1, ex_y1), (ex_x2, ex_y2), (0, 0, 255), 2)
    cv2.line(annotated_frame, (0, slice_h), (w, slice_h), (0, 0, 255), 2)
    cv2.line(annotated_frame, (0, h-slice_h), (w, h-slice_h), (0, 0, 255), 2)

    # 画像表示（2秒以内）
    if display_active:
        if now - display_start_time <= 2.0:
            resized_img = cv2.resize(display_img, (resized_w, resized_h))
            x, y = display_pos
            annotated_frame[y:y+resized_h, x:x+resized_w] = resized_img
        else:
            display_active = False

    # 結果表示
    cv2.imshow("YOLOv8 Detection (Selective Area)", annotated_frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
