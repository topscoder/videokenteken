import argparse
import os
import sys
from datetime import datetime

from utils import video_downloader, video_reader, config
from db import db_utils
from detectors.yolo_detector import YoloPlateDetector
from ocr.ocr_utils import extract_text_from_image

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

    # Download video if URL provided
    local_video_path = args.video_path
    if args.video_url:
        print(f"[INFO] Downloading video from: {args.video_url}")
        local_video_path = video_downloader.download_video(args.video_url, "downloads")
        print(f"[INFO] Video downloaded to: {local_video_path}")

    # Init database
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

    print("[INFO] Processing complete.")

if __name__ == "__main__":
    main()