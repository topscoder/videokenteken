# detectors/yolo_detector.py

from ultralytics import YOLO
import cv2

class YoloPlateDetector:
    """
    A YOLO-based license plate detector. Requires a model
    trained specifically to detect license plates.
    """

    def __init__(self, model_path, conf_threshold=0.5):
        """
        :param model_path: Path to the YOLO weights file (trained for license plates).
        :param conf_threshold: Confidence threshold.
        """
        self.model_path = model_path
        self.conf_threshold = conf_threshold
        self.model = YOLO(self.model_path)  # load YOLO model

        # Export the model to TFLite format
        self.model.export(format='tflite')
        self.model = YOLO(self.model_path.replace('.pt', '.onnx'))  # load TFLite model

    def detect_plates(self, frame):
        """
        Runs detection on a single frame (numpy array).

        :param frame: np.ndarray in BGR format
        :return: list of detections
                 each detection = (x1, y1, x2, y2, confidence)
        """
        # YOLOv8 expects an RGB image
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = self.model.predict(source=rgb_frame, imgsz=640, conf=self.conf_threshold)

        detections = []
        # results is typically a list; we'll take the first (and only) item
        for box in results[0].boxes:
            # box.xyxy[0] => [x1, y1, x2, y2]
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            conf = box.conf[0].item()
            cls_id = int(box.cls[0].item())
            # Optionally, we can check if the detection class matches 'plate' if our model has that label
            # but for a single-class model, we'll just take them all here.
            # if your model has multiple classes, filter by the correct class index or name
            detections.append((x1, y1, x2, y2, conf))

        return detections
