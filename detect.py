# YOLOv8 顔判定付き＋物体検出
# ── クラス別アラート画像を個別時間管理し、前回検出位置との差分で速度を計算して横方向に自動移動 ──

import cv2
import numpy as np
import time
from ultralytics import YOLO

# ───────────── モデル読み込み ─────────────
main_model = YOLO("runs/detect/train/weights/best_29.pt")     # アイテム検出
face_model = YOLO("runs/detect/train/weights/best_30.pt")    # 顔検出（←Xボタン判定用）

# ───────────── クラス名 → 表示画像 ─────────────
class2image = {
    "Piranha-Plant": cv2.imread("Piranha-Plant.png"),
    "Super-Horn":    cv2.imread("Super-Horn.png"),
    "FB":            cv2.imread("FB.png"),
    "Boomerang":     cv2.imread("Boomerang.png"),
    "Minacle-Eight": cv2.imread("Minacle-Eight.png"),
    "green-shell3":  cv2.imread("Green-Shell3.png"),
}

# ───────────── 表示状態管理（クラス別） ─────────────
# active : 表示中かどうか
# start_time : 表示開始時刻
# pos : （x, y）左上座標
# scale : 拡大率
# prev_x, prev_t : 前回検出時の中心X座標と時刻（速度計算用）
# vx : ピクセル／秒  （-v_max ～ +v_max）
display_info = {
    cls: {
        "active": False,
        "start_time": 0,
        "pos": (0, 0),
        "scale": 1.0,
        "prev_x": None,
        "prev_t": None,
        "vx": 0.0,
    } for cls in class2image
}

# ───────────── カメラ準備 ─────────────
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise IOError("キャプチャデバイスが開けません")

ret, frame = cap.read()
if not ret:
    raise RuntimeError("カメラからフレームが取得できません")

# ✅ VideoWriterを追加（保存ファイル名、コーデック、FPS、フレームサイズ）
fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # または 'XVID', 'avc1', 'MJPG'
out = cv2.VideoWriter('output_video_new21.mp4', fourcc, 30.0, (frame.shape[1], frame.shape[0]))


# ───────────── 定数 ─────────────
h, w = frame.shape[:2]
CONF_TH     = 0.45     # 物体検出しきい値
FACE_TH     = 0.45      # 顔検出しきい値
ALERT_SIZE  = (150, 150)
SHOW_SEC    = 2.5       # 画像を表示する秒数
V_MAX_PX    = 400.0     # 速度の絶対最大値(px/秒)

# 顔検出赤枠 
# (マメであればクッパまで枠内に入る: cx_f, cy_f  = w//2 + 100, h//2 + 200, fw, fh = 430, 360)
cx_f, cy_f  = w//2 + 100, h//2 + 200
fw, fh      = 430, 360
fx1, fy1    = cx_f - fw//2, cy_f - fh//2
fx2, fy2    = cx_f + fw//2, cy_f + fh//2

# アイテム検出マスク（上下カット）
upper_y, lower_y = int(h*0.23), int(h*0.8)

# ───────────── メインループ ─────────────
while True:
    ok, frame = cap.read()
    if not ok:
        print("フレーム取得失敗"); break

    now = time.time()
    annotated = frame.copy()

    # ---------- 1) 顔検出 ----------
    face_crop = frame[fy1:fy2, fx1:fx2]
    face_boxes = face_model(face_crop)[0].boxes
    face_in = any(float(b.conf) >= FACE_TH for b in face_boxes)

    # ---------- 2) アイテム検出 ----------
    if face_in:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!") 
        # Xボタンが押されていれば推論
        mask = np.ones((h, w), np.uint8)*255
        mask[:upper_y, :] = 0
        mask[lower_y:, :] = 0
        mask[fy1:fy2, fx1:fx2] = 0                       # 顔検出枠もマスク
        roi = cv2.bitwise_and(frame, frame, mask=mask)

        results = main_model(roi)[0]
        for b in results.boxes:
            if float(b.conf) < CONF_TH: continue
            x1,y1,x2,y2 = b.xyxy[0].cpu().numpy()
            cls_name    = results.names[int(b.cls)]

            # バウンディングボックス可視化 for debug
            # cv2.rectangle(annotated,(int(x1),int(y1)),(int(x2),int(y2)),(0,255,0),2)
            # cv2.putText(annotated,f"{cls_name} {float(b.conf):.2f}",(int(x1),int(y1)-10),
            #             cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,255,0),2)

            # 画像登録があるクラスのみ
            if cls_name in class2image and class2image[cls_name] is not None:
                cx_box = (x1+x2)/2                       # 今回中心X
                info   = display_info[cls_name]

                # ----- 速度計算 -----
                if info["prev_x"] is not None:           # 前回があれば速度計算
                    dt = max(now - info["prev_t"], 1e-3)
                    vx = np.clip((cx_box - info["prev_x"])/dt, -V_MAX_PX, V_MAX_PX)
                else:
                    vx = 0.0
                info.update(prev_x=cx_box, prev_t=now, vx=vx)

                # ----- 表示位置 & 状態更新 -----
                img_w,img_h = ALERT_SIZE
                pos_x = int(np.clip(cx_box - img_w//2, 0, w-img_w))
                pos_y = h - img_h - 10
                info.update(active=True, start_time=now, pos=(pos_x,pos_y), scale=1.0)

    # ---------- 3) 全クラス画像描画 ----------
    for cls, info in display_info.items():
        if not info["active"]: continue
        dt_show = now - info["start_time"]

        if dt_show <= SHOW_SEC:
            # 速度による横スライド
            dx = int(info["vx"] * dt_show)
            x0,y0 = info["pos"]
            x = int(np.clip(x0 + dx, 0, w-ALERT_SIZE[0]))
            y = y0
            img = cv2.resize(class2image[cls], ALERT_SIZE)
            annotated[y:y+ALERT_SIZE[1], x:x+ALERT_SIZE[0]] = img
        else:
            # 表示終了：active解除 & prev_xもリセット
            info.update(active=False, prev_x=None, prev_t=None, vx=0.0)

    # ---------- 4) デバッグ用枠 ----------
    # cv2.rectangle(annotated,(fx1,fy1),(fx2,fy2),(0,0,255),2)
    # cv2.line(annotated,(0,upper_y),(w,upper_y),(0,0,255),2)
    # cv2.line(annotated,(0,lower_y),(w,lower_y),(0,0,255),2)

    # ---------- 5) 表示 ----------
    cv2.imshow("YOLOv8 Detection (Face‑Gated, Velocity Overlay)", annotated)

    # ✅ 録画処理を追加
    out.write(annotated)

    if cv2.waitKey(1) & 0xFF == ord("q"): break

cap.release()
out.release() 
cv2.destroyAllWindows()
