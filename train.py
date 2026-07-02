from ultralytics import YOLO

model = YOLO("yolov8n.pt")

model.train(
    data='datasets/Item_Detection.v4-original-v1.yolov8/data.yaml',
    epochs=100,
    imgsz=640,
    scale=0.4,           
    shear=2,             
    perspective=0.0005,  
)

# -----------------------item-detection-model-----------------------
# data='datasets/Item_Alert.v5-pre-minacle8-aug-v2.yolov8/data.yaml',
# Results saved to runs/detect/train10
# only aug


# Item Detection.v1i.yolov8
# Results saved to runs/detect/train12
# proprocessed *5 / 


# **Item_Detection.v2-pre-8-include-nullimage-v1.yolov8
# Results saved to runs/detect/train13
# null images / proprocessed *5 / 


# **Item_Detection.v3-full-items-v1.yolov8
# Results saved to runs/detect/train14

# **Item_Detection.v4-original-v1.yolov8
# Model summary (fused): 72 layers, 3,005,843 parameters, 0 gradients, 8.1 GFLOPs
#                  Class     Images  Instances      Box(P          R      mAP50  mAP50-95): 100%|██████████| 8/8 [00:00<00:00, 13.30it/s]
#                    all        255        157      0.987      0.987      0.993       0.75
# Speed: 0.1ms preprocess, 0.6ms inference, 0.0ms loss, 0.7ms postprocess per image
# only crop leftside


# ****Item_Detection.v7-full-items-v3.yolov8
# 
# full null images

# 100 epochs completed in 0.373 hours.
# Optimizer stripped from runs/detect/train21/weights/last.pt, 6.3MB
# Optimizer stripped from runs/detect/train21/weights/best.pt, 6.3MB

# Validating runs/detect/train21/weights/best.pt...
# Ultralytics 8.3.116 🚀 Python-3.11.7 torch-2.7.0+cu126 CUDA:0 (NVIDIA GeForce RTX 3090, 24260MiB)
# Model summary (fused): 72 layers, 3,006,818 parameters, 0 gradients, 8.1 GFLOPs
#                  Class     Images  Instances      Box(P          R      mAP50  mAP50-95): 100%|██████████| 5/5 [00:00<00:00,  8.85it/s]
#                    all        134        133      0.863      0.751       0.81      0.488
#              Boomerang         29         29       0.95      0.652      0.792      0.427
#                     FB         26         38      0.852      0.658      0.705      0.354
#          Minacle-Eight         11         15      0.742      0.667      0.735      0.478
#          Piranha-Plant         22         22      0.767      0.682       0.73      0.392
#             Super-Horn         20         20      0.915       0.85      0.901      0.565
#           green-shell3          9          9      0.952          1      0.995      0.715
# Speed: 0.1ms preprocess, 1.0ms inference, 0.0ms loss, 0.4ms postprocess per image
# Results saved to runs/detect/train21




# **Item_Detection.v8-full-items-v4.yolov8
# no null images
# 50 epochs completed in 0.160 hours.
# Optimizer stripped from runs/detect/train24/weights/last.pt, 6.3MB
# Optimizer stripped from runs/detect/train24/weights/best.pt, 6.3MB

# Validating runs/detect/train24/weights/best.pt...
# Ultralytics 8.3.116 🚀 Python-3.11.7 torch-2.7.0+cu126 CUDA:0 (NVIDIA GeForce RTX 3090, 24260MiB)
# Model summary (fused): 72 layers, 3,006,818 parameters, 0 gradients, 8.1 GFLOPs
#                  Class     Images  Instances      Box(P          R      mAP50  mAP50-95): 100%|██████████| 4/4 [00:00<00:00, 11.62it/s]
#                    all        116        133      0.834      0.746      0.793      0.454
#              Boomerang         29         29      0.867      0.655      0.724      0.398
#                     FB         26         38      0.821      0.711      0.747       0.33
#          Minacle-Eight         11         15      0.747       0.59      0.643      0.398
#          Piranha-Plant         22         22      0.739      0.644      0.737      0.316
#             Super-Horn         20         20      0.898      0.876      0.911      0.597
#           green-shell3          9          9      0.932          1      0.995      0.687
# Speed: 0.1ms preprocess, 0.6ms inference, 0.0ms loss, 0.3ms postprocess per image
# Results saved to runs/detect/train24

# Item_Detection.v9-original-v2.yolov8
# orignal images *2
# Validating runs/detect/train29/weights/best.pt...
# Ultralytics 8.3.116 🚀 Python-3.11.7 torch-2.7.0+cu126 CUDA:0 (NVIDIA GeForce RTX 3090, 24260MiB)
# Model summary (fused): 72 layers, 3,006,818 parameters, 0 gradients, 8.1 GFLOPs
#                  Class     Images  Instances      Box(P          R      mAP50  mAP50-95): 100%|██████████| 5/5 [00:00<00:00, 11.47it/s]
#                    all        134        133      0.828      0.778      0.795       0.49
#              Boomerang         29         29       0.84      0.655      0.714      0.415
#                     FB         26         38      0.733       0.65      0.718      0.318
#          Minacle-Eight         11         15      0.796       0.78      0.735      0.511
#          Piranha-Plant         22         22      0.703      0.682      0.699      0.384
#             Super-Horn         20         20      0.896        0.9       0.91      0.557
#           green-shell3          9          9          1      0.999      0.995      0.755
# Speed: 0.1ms preprocess, 0.6ms inference, 0.0ms loss, 1.4ms postprocess per image
# Results saved to runs/detect/train29


# -----------------------face-detection-model-----------------------


# Face-Detection.v1-not-include-nullimage-v1.yolov8
# Results saved to runs/detect/train15

# Face-Detection.v2-include-nullimage-v1.yolov8
# Results saved to runs/detect/train16

# Face-Detection.v3-include-nullimage-v2.yolov8
# Results saved to runs/detect/train19
# almost full include null images




# Face-Detection.v4-include-nullimage-v3.yolov8
# 50% null images


# 50 epochs completed in 0.265 hours.
# Optimizer stripped from runs/detect/train27/weights/last.pt, 6.2MB
# Optimizer stripped from runs/detect/train27/weights/best.pt, 6.2MB

# Validating runs/detect/train27/weights/best.pt...
# Ultralytics 8.3.116 🚀 Python-3.11.7 torch-2.7.0+cu126 CUDA:0 (NVIDIA GeForce RTX 3090, 24260MiB)
# Model summary (fused): 72 layers, 3,005,843 parameters, 0 gradients, 8.1 GFLOPs
#                  Class     Images  Instances      Box(P          R      mAP50  mAP50-95): 100%|██████████| 8/8 [00:00<00:00, 12.59it/s]
#                    all        255        157      0.987      0.994      0.993      0.763
# Speed: 0.1ms preprocess, 0.6ms inference, 0.0ms loss, 0.5ms postprocess per image
# Results saved to runs/detect/train27


# Face-Detection.v5-original-v1.yolov8
# 100 epochs completed in 0.164 hours.
# Optimizer stripped from runs/detect/train30/weights/last.pt, 6.3MB
# Optimizer stripped from runs/detect/train30/weights/best.pt, 6.3MB

# Validating runs/detect/train30/weights/best.pt...
# Ultralytics 8.3.116 🚀 Python-3.11.7 torch-2.7.0+cu126 CUDA:0 (NVIDIA GeForce RTX 3090, 24260MiB)
# Model summary (fused): 72 layers, 3,005,843 parameters, 0 gradients, 8.1 GFLOPs
#                  Class     Images  Instances      Box(P          R      mAP50  mAP50-95): 100%|██████████| 7/7 [00:00<00:00, 11.61it/s]
#                    all        219        157      0.987      0.994      0.992      0.765
# Speed: 0.1ms preprocess, 0.6ms inference, 0.0ms loss, 0.8ms postprocess per image
# Results saved to runs/detect/train30