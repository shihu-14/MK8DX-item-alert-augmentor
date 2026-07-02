# YOLOv8 顔専用モデルによるリアルタイム顔判定付き物体検出（クラス別画像表示対応）

import cv2
import numpy as np
import time
from ultralytics import YOLO

# main model
main_model = YOLO("runs/detect/train/weights/best.pt")

# face recognition model
face_model = YOLO("yolov8n-face.pt")

# class name -> alert images
class2image = {
    "Piranha-Plant": cv2.imread("assets/icons/alerts/Piranha-Plant.png"),
    "Super-Horn": cv2.imread("assets/icons/alerts/Super-Horn.png"),
    "FB": cv2.imread("assets/icons/alerts/FB.png"),
    "Boomerang": cv2.imread("assets/icons/alerts/Boomerang.png"),
    "Minacle-Eight": cv2.imread("assets/icons/alerts/Minacle-Eight.png"),
    # others..
}

# start capture
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise IOError("キャプチャデバイスが開けません")

ret, frame = cap.read()
if not ret:
    raise RuntimeError("カメラからフレームが取得できません")


# const values
h, w = frame.shape[:2]
fps = 30
CONF_THRESHOLD = 0.25
FACE_CONF_THRESHOLD = 0.15
ALERT_IMAGE_SIZE = (50, 50)

# bounding-box for face-recognition
center_x, center_y = w//2 + 100, h//2 + 100
box_width, box_height = 400, 270
ex_x1 = center_x - box_width // 2
ex_y1 = center_y - box_height // 2
ex_x2 = center_x + box_width // 2
ex_y2 = center_y + box_height // 2
# bounding-box for item-recognition
upper, lower = h//5, h*70//100

# values for alert images
display_active = False
display_start_time = 0
display_pos = (0, 0)
display_scale = 1.0
display_img = None

while True:
    ret, frame = cap.read()
    if not ret:
        print("フレーム取得失敗")
        break

    annotated_frame = frame.copy()
    now = time.time()

    # cropped for face-recognition
    cropped_face_region = frame[ex_y1:ex_y2, ex_x1:ex_x2]
    face_results = face_model(cropped_face_region)
    face_boxes = face_results[0].boxes

    # if face is detected (pressed X button)
    face_in_area = False
    for box in face_boxes:
        conf = float(box.conf)
        if conf >= FACE_CONF_THRESHOLD:
            face_in_area = True
            break

    boxes = []
    if face_in_area:
        # mask for item-recognition
        mask = np.ones((h, w), dtype=np.uint8) * 255
        mask[0:upper, :] = 0
        mask[lower:h, :] = 0
        mask[ex_y1:ex_y2, ex_x1:ex_x2] = 0
        masked_frame = cv2.bitwise_and(frame, frame, mask=mask)
        print("mask applied!!!!!!!!!!!!")
        # main model
        results = main_model(masked_frame)
        boxes = results[0].boxes

        for box in boxes:
            if box.conf >= CONF_THRESHOLD:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                cls_id = int(box.cls)
                conf = float(box.conf)
                label_name = results[0].names[cls_id]
                print("detected!!!!!!!!!!!")
                # for debug
                cv2.rectangle(annotated_frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                label = f"{label_name} {conf:.2f}"
                cv2.putText(annotated_frame, label, (int(x1), int(y1) - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                area = (x2 - x1) * (y2 - y1)
                scale = 1
                # scale = min(max(0.2, 20000 / (area + 1)), 2.0) # scale: 0.2 ~ 2.0

                center_x_box = (x1 + x2) / 2
                if label_name in class2image and class2image[label_name] is not None:
                    display_img = class2image[label_name]
                else:
                    display_img = None

                if display_img is not None:
                    resized_w = int(ALERT_IMAGE_SIZE[0] * scale)
                    resized_h = int(ALERT_IMAGE_SIZE[1] * scale)
                    # draw image in center and bottom
                    display_pos = (max(0, min(w - resized_w, center_x_box - resized_w // 2)), h - resized_h - 10)
                    display_scale = scale
                    display_start_time = now
                    display_active = True

    # draw bounding-box for debug
    cv2.rectangle(annotated_frame, (ex_x1, ex_y1), (ex_x2, ex_y2), (0, 0, 255), 2)
    cv2.line(annotated_frame, (0, upper), (w, upper), (0, 0, 255), 2)
    cv2.line(annotated_frame, (0, lower), (w, lower), (0, 0, 255), 2)

    # draw alert images
    if display_active and display_img is not None:
        if now - display_start_time <= 2.0:
            resized_img = cv2.resize(display_img, (resized_w, resized_h))
            x, y = map(int, display_pos)
            annotated_frame[y:y+resized_h, x:x+resized_w] = resized_img
        else:
            display_active = False

    # display
    cv2.imshow("YOLOv8 Detection (Face-Gated)", annotated_frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
