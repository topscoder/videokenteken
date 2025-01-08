import argparse
import os
import sys
import cv2  # Import OpenCV for duration calculation
from datetime import datetime

from utils import video_downloader, video_reader, config
from db import db_utils
from detectors.yolo_detector import YoloPlateDetector
from ocr.ocr_utils import extract_text_from_image

def get_video_duration(video_path):
    """
    Retrieve the total duration of the video in seconds using OpenCV.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Unable to open video file {video_path}")
        return None
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    cap.release()
    if fps > 0:
        return frame_count / fps
    else:
        return None

def main():
    parser = argparse.ArgumentParser(
        description="License Plate Detection and OCR from YouTube/Local Videos."
    )
    parser.add_argument(
        "--video_url",
        help="URL of the YouTube video (if you want to download)",
        default=None
    )
    parser.add_argument(
        "--video_path",
        help="Local path to video file (if already downloaded)",
        default=None
    )
    parser.add_argument(
        "--confidence_threshold",
        help="Confidence threshold for plate detection (0.0 - 1.0)",
        default=0.5,
        type=float
    )
    parser.add_argument(
        "--frame_skip",
        help="Number of frames to skip between detection attempts",
        default=5,
        type=int
    )
    args = parser.parse_args()

    # Ensure we have either a URL or a local path
    if not args.video_url and not args.video_path:
        print("Error: Must provide --video_url or --video_path.")
        sys.exit(1)

    # Record start time for processing
    start_time = datetime.now()

    # Download video if URL provided
    local_video_path = args.video_path
    if args.video_url:
        print(f"[INFO] Downloading video from: {args.video_url}")
        local_video_path = video_downloader.download_video(args.video_url, "downloads")
        print(f"[INFO] Video downloaded to: {local_video_path}")

    # Initialize database
    db_session = db_utils.init_db(config.DB_PATH)

    # Create or retrieve video record
    video_id = db_utils.insert_video_record(
        db_session,
        url=args.video_url or local_video_path,
        local_path=local_video_path,
        processing_date=datetime.now()
    )

    # Initialize plate detector
    plate_detector = YoloPlateDetector(model_path=config.DEFAULT_MODEL_PATH, conf_threshold=args.confidence_threshold)

    # Process video frames
    video_reader.process_video(
        video_path=local_video_path,
        detector=plate_detector,
        ocr_function=extract_text_from_image,
        db_session=db_session,
        video_id=video_id,
        frame_skip=args.frame_skip
    )

    # Record end time after processing
    end_time = datetime.now()

    # Calculate total processing time
    total_processing_time = end_time - start_time

    # Get video duration
    video_duration = get_video_duration(local_video_path)

    print("[INFO] Processing complete.")
    print(f"[INFO] Total processing time: {total_processing_time}")
    if video_duration is not None:
        # Format duration as HH:MM:SS
        hours = int(video_duration // 3600)
        minutes = int((video_duration % 3600) // 60)
        seconds = int(video_duration % 60)
        print(f"[INFO] Total video duration: {hours:02d}:{minutes:02d}:{seconds:02d} (HH:MM:SS)")
    else:
        print("[WARN] Unable to determine video duration.")

if __name__ == "__main__":
    main()
