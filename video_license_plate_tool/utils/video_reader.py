# utils/video_reader.py

from db.db_utils import insert_plate_record
import cv2
import json
import logging
import queue
import threading


batch_size = 10

def frame_loader(cap, frame_queue, frame_skip):
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_count % frame_skip == 0:
            frame_queue.put((frame_count, frame))
        frame_count += 1
    frame_queue.put(None)  # Sentinel value to signal end of video


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
    frame_queue = queue.Queue(maxsize=batch_size * 2)  # Buffer size can be adjusted
    loader_thread = threading.Thread(target=frame_loader, args=(cap, frame_queue, frame_skip))
    loader_thread.daemon = True  # Ensures thread exits if main program exits
    loader_thread.start()

    frame_count = 0
    batch_frames = []
    batch_indices = []

    while True:
        item = frame_queue.get()  # Retrieve frame from queue
        if item is None:
            # No more frames to process
            break
        idx, frame = item
        batch_frames.append(frame)
        batch_indices.append(idx)

        if len(batch_frames) == batch_size:
            # Process batch as before
            detections_list = detector.detect_batch(batch_frames)
            for b_idx, detections in enumerate(detections_list):
                ts = batch_indices[b_idx] / fps
                for (x1, y1, x2, y2, conf) in detections:
                    plate_crop = batch_frames[b_idx][int(y1):int(y2), int(x1):int(x2)]
                    plate_text = ocr_function(plate_crop)
                    if plate_text:
                        bbox_dict = {"x1": float(x1), "y1": float(y1), "x2": float(x2), "y2": float(y2)}
                        insert_plate_record(
                            session=db_session,
                            video_id=video_id,
                            timestamp=ts,
                            plate_text=plate_text,
                            confidence=float(conf),
                            bbox=json.dumps(bbox_dict)
                        )
            batch_frames.clear()
            batch_indices.clear()

    # Process remaining frames in batch_frames if any
    if batch_frames:
        detections_list = detector.detect_batch(batch_frames)
        for b_idx, detections in enumerate(detections_list):
            ts = batch_indices[b_idx] / fps
            for (x1, y1, x2, y2, conf) in detections:
                plate_crop = batch_frames[b_idx][int(y1):int(y2), int(x1):int(x2)]
                plate_text = ocr_function(plate_crop)
                if plate_text:
                    bbox_dict = {"x1": float(x1), "y1": float(y1), "x2": float(x2), "y2": float(y2)}
                    insert_plate_record(
                        session=db_session,
                        video_id=video_id,
                        timestamp=ts,
                        plate_text=plate_text,
                        confidence=float(conf),
                        bbox=json.dumps(bbox_dict)
                    )

    cap.release()
    loader_thread.join()  # Ensure the loader thread finishes
