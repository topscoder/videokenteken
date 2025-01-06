# utils/video_reader.py

import logging
import cv2
from db.db_utils import insert_plate_record
import json

def process_video(video_path, detector, ocr_function, db_session, video_id, frame_skip=5):
    """
    Iterate through video frames, detect plates, run OCR, and insert results into DB.
    :param video_path: str, path to local video
    :param detector: an object with .detect_plates(frame) -> list of bounding boxes
    :param ocr_function: function that takes cropped image -> text
    :param db_session: DB session for inserts
    :param video_id: int, ID of the corresponding video in DB
    :param frame_skip: int, how many frames to skip between detections
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"[ERROR] Cannot open video: {video_path}")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Only analyze every Nth frame
        if frame_count % frame_skip == 0:
            detections = detector.detect_plates(frame)
            timestamp_sec = frame_count / fps

            for (x1, y1, x2, y2, conf) in detections:
                # Crop bounding box
                plate_crop = frame[int(y1):int(y2), int(x1):int(x2)]
                plate_text = ocr_function(plate_crop)
                
                # if len(plate_text.strip()) >= 6:
                if len(plate_text.strip()) == 6:
                    print(f"Detected plate: {plate_text} | Confidence: {conf:.2f}")

                    # Insert record if we got something
                    if plate_text:
                        bbox_dict = {
                            "x1": float(x1),
                            "y1": float(y1),
                            "x2": float(x2),
                            "y2": float(y2),
                        }
                        insert_plate_record(
                            session=db_session,
                            video_id=video_id,
                            timestamp=timestamp_sec,
                            plate_text=plate_text,
                            confidence=float(conf),
                            bbox=json.dumps(bbox_dict)
                        )

        frame_count += 1

    cap.release()
