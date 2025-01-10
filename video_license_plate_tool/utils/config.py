# utils/config.py

import os

# Default database path
DB_PATH = os.path.join(os.getcwd(), "license_plate_data.db")

# Default YOLO model path (replace with your own trained model)
DEFAULT_MODEL_PATH = "models/yolov9_easyocr_best.pt"
