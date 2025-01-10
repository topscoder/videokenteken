# detectors/yolo_detector.py
from ultralytics import YOLO
import cv2
import torch

class YoloPlateDetector:
    """
    A YOLO-based license plate detector optimized for GPU with mixed precision.
    """

    def __init__(self, model_path="plate_detection.pt", conf_threshold=0.5):
        self.model_path = model_path
        self.conf_threshold = conf_threshold
        
        # Load the YOLO model and move it to GPU if available
        self.model = YOLO(self.model_path)
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model.model.to(device)

        # Set model to half precision if using GPU
        if device == 'cuda':
            self.model.model.half()

        # Export the model to TFLite format
        # self.model.export(format='tflite')
        # self.model = YOLO(self.model_path.replace('.pt', '.onnx'))  # load TFLite model

    def detect_plates(self, frame):
        """
        Runs detection on a single frame with mixed precision.
        """
        # Convert frame to RGB as YOLO expects
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Use torch.autocast for mixed precision inference on GPU
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        with torch.cuda.amp.autocast(enabled=(device == 'cuda')):
            results = self.model.predict(source=rgb_frame, imgsz=640, conf=self.conf_threshold)

        detections = []
        for box in results[0].boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            conf = box.conf[0].item()
            detections.append((x1, y1, x2, y2, conf))
        return detections

    def detect_batch(self, frames):
        """
        Runs detection on a batch of frames.
        :param frames: list of np.ndarray frames in BGR format.
        :return: list of detections for each frame, where each detection is a list of (x1, y1, x2, y2, confidence).
        """
        # Convert each frame to RGB
        rgb_frames = [cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) for frame in frames]
        
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        with torch.cuda.amp.autocast(enabled=(device == 'cuda')):
            results = self.model.predict(source=rgb_frames, imgsz=640, conf=self.conf_threshold)
        
        all_detections = []
        for result in results:
            detections = []
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                conf = box.conf[0].item()
                detections.append((x1, y1, x2, y2, conf))
            all_detections.append(detections)
        return all_detections
