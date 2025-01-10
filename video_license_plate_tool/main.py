import argparse
import os
import sys
import cv2  # OpenCV for duration calculation
from datetime import datetime

from utils import video_downloader, video_reader, config
from db import db_utils
from detectors.yolo_detector import YoloPlateDetector
from ocr.ocr_utils import extract_text_from_image
from db.models import Video

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

def process_single_video(db_session, video_url, video_path, confidence_threshold, frame_skip, force, skip):
    """
    Process a single video given by video_url or video_path.
    Applies reprocessing logic based on the 'force' flag.
    """
    # Record start time for processing
    start_time = datetime.now()

    # Check if the video was processed before
    existing_video = None
    if video_url:
        existing_video = db_session.query(Video).filter(Video.url == video_url).first()
    elif video_path:
        existing_video = db_session.query(Video).filter(Video.local_path == video_path).first()

    if existing_video and not force and not skip:
        response = input("This video has been processed before. Do you want to proceed with a new analysis? (y/n): ")
        if response.lower() != 'y':
            print("Skipping video reprocessing.")
            return
    elif existing_video and skip:
        print("Skipping video reprocessing.")
        return

    # Download video if URL provided and local path not given
    if video_url and not video_path:
        print(f"[INFO] Downloading video from: {video_url}")
        video_path = video_downloader.download_video(video_url, "downloads")
        print(f"[INFO] Video downloaded to: {video_path}")

    # Create or retrieve video record
    video_id = db_utils.insert_video_record(
        db_session,
        url=video_url or video_path,
        local_path=video_path,
        processing_date=datetime.now()
    )

    # Initialize plate detector
    plate_detector = YoloPlateDetector(model_path=config.DEFAULT_MODEL_PATH, conf_threshold=confidence_threshold)

    # Process video frames
    video_reader.process_video(
        video_path=video_path,
        detector=plate_detector,
        ocr_function=extract_text_from_image,
        db_session=db_session,
        video_id=video_id,
        frame_skip=frame_skip
    )

    # Record end time after processing
    end_time = datetime.now()

    # Calculate total processing time
    total_processing_time = end_time - start_time

    # Get video duration
    video_duration = get_video_duration(video_path)

    print("[INFO] Processing complete.")

    # Remove the video file if it was downloaded
    if video_url and video_path:
        os.remove(video_path)
        print(f"[INFO] Removed downloaded video file: {video_path}")

    print(f"[INFO] Total processing time: {total_processing_time}")
    if video_duration is not None:
        # Format duration as HH:MM:SS
        hours = int(video_duration // 3600)
        minutes = int((video_duration % 3600) // 60)
        seconds = int(video_duration % 60)
        print(f"[INFO] Total video duration: {hours:02d}:{minutes:02d}:{seconds:02d} (HH:MM:SS)")
    else:
        print("[WARN] Unable to determine video duration.")

parser = argparse.ArgumentParser(
    description="License Plate Detection and OCR from YouTube/Local Videos."
)
parser.add_argument(
    "--video_url",
    help="URL of a single YouTube video (if you want to download)",
    default=None
)
parser.add_argument(
    "--video_path",
    help="Local path to a single video file (if already downloaded)",
    default=None
)
parser.add_argument(
    "--video_list_file",
    help="Path to text file with multiple video URLs",
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
parser.add_argument(
    "--force",
    help="Force reprocessing without asking if video was processed before",
    action="store_true"
)
parser.add_argument(
    "--skip",
    help="Skip reprocessing if video was processed before",
    action="store_true"
)

args = parser.parse_args()

# Ensure at least one video source is provided
if not args.video_list_file and not args.video_url and not args.video_path:
    print("Error: Must provide --video_url, --video_path or --video_list_file.")
    sys.exit(1)

# Initialize database session once for all processing
db_session = db_utils.init_db(config.DB_PATH)

if args.video_list_file:
    # Read video URLs from the provided text file
    try:
        with open(args.video_list_file, "r") as f:
            video_urls = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"Error reading video list file: {e}")
        sys.exit(1)

    for url in video_urls:
        print(f"\n[INFO] Starting processing for video: {url}")
        process_single_video(
            db_session=db_session,
            video_url=url,
            video_path=None,
            confidence_threshold=args.confidence_threshold,
            frame_skip=args.frame_skip,
            force=args.force,
            skip=args.skip
        )
else:
    # Process a single video based on provided URL or path
    process_single_video(
        db_session=db_session,
        video_url=args.video_url,
        video_path=args.video_path,
        confidence_threshold=args.confidence_threshold,
        frame_skip=args.frame_skip,
        force=args.force,
        skip=args.skip
    )

db_session.close()
