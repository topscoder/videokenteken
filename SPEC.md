
# Technical Specification: Video License Plate Analysis Tool

## 1. Overview

The purpose of this tool is to:
1. **Download** and/or **process** videos (preferably from YouTube).
2. **Identify** visible license plates in video frames.
3. **Extract** the text from these license plates.
4. **Store** the results—license plate string, confidence score, video URL, and frame timestamps—in a database.
5. **Allow** configuration of the confidence threshold so that we can calibrate for minimal false positives vs. coverage.

This specification outlines the steps, technologies, and design choices needed to create a robust solution that runs on a macOS environment with an Intel Core i9 CPU, and available GPUs (Radeon Pro 560X and Intel UHD Graphics 630).

---

## 2. Requirements

1. **Operating System**: macOS (Intel Core i9 CPU)
   - GPU: Radeon Pro 560X (4 GB) and Intel UHD Graphics 630 (1536 MB)
2. **Primary Language**: Python 3.8+ 
3. **Libraries & Tools**:
   - Video processing: [FFmpeg](https://ffmpeg.org/) and/or [OpenCV](https://opencv.org/)
   - Object detection / Model: YOLO, or any CNN-based detection framework that supports license plate detection
   - OCR for plate text recognition: [Tesseract](https://github.com/tesseract-ocr/tesseract) or specialized ALPR (Automatic License Plate Recognition) frameworks
   - YouTube Video Downloading: [pytube](https://github.com/pytube/pytube) or [youtube-dl](https://github.com/ytdl-org/youtube-dl)
   - Database: SQLite (for local quick storage) or PostgreSQL/MySQL if needed for scale
4. **Confidence Threshold**: A configurable numeric parameter for filtering out low-probability detections.
5. **Data to Store**:
   - Video metadata: video URL, local path
   - Timestamps of detections
   - Plate text (string)
   - Detection confidence
   - Possibly bounding box coordinates for debugging

---

## 3. Architecture & Flow

### 3.1 High-Level Workflow

1. **Video Acquisition**: 
   - User provides a YouTube URL (or local video file path).
   - Tool downloads the video (if YouTube URL) to a local directory or reads existing file.

2. **Frame Extraction**:
   - The tool either processes the video frame-by-frame or at a chosen interval (e.g., every N frames/seconds).
   - Extract frames using OpenCV or FFmpeg.

3. **License Plate Detection**:
   - A pre-trained license plate detection model (e.g., YOLO-based or another approach) runs on each extracted frame.
   - If a bounding box is found for a license plate, record:
     - The bounding box coordinates
     - The detection confidence

4. **Text Recognition (OCR)**:
   - Once a bounding box is found with high-enough confidence, pass that region to an OCR engine (e.g., Tesseract).
   - Extract the text of the plate.

5. **Result Filtering**:
   - Compare the detection confidence with the user-defined threshold. 
   - If above threshold, accept the result; otherwise discard.

6. **Database Storage**:
   - Store the following data:
     - Video reference (URL or ID)
     - Timestamp of frame in the video
     - Plate text
     - Detection confidence
     - (Optional) bounding box coordinates

7. **Result Output / Logging**:
   - Provide a summary or log file with discovered plates, timestamps, and confidence levels.
   - Provide an interface (CLI, web, or otherwise) to query results from the database.

---

## 4. Detailed Implementation Steps

### 4.1 Environment Setup
1. **Install Python 3.8+** (if not already on macOS).
2. **Install Libraries**:
   - `OpenCV` (e.g., `pip install opencv-python`)
   - `pytube` or `youtube-dl`
   - `ffmpeg` (e.g., `brew install ffmpeg`)
   - `Tesseract` (e.g., `brew install tesseract`)
   - `PyTesseract` (Python wrapper: `pip install pytesseract`)
   - `SQLAlchemy` or any Python DB-API connector if using SQLite (e.g., `sqlite3` is included in Python by default).
3. **Model Installation** (Optional, if using YOLO):
   - You can either download a pre-trained license plate YOLO model or train your own. 
   - For example, if using YOLOv5/YOLOv8: `pip install ultralytics` (for YOLOv8).

### 4.2 Video Acquisition
1. **YouTube Download**:
   - Use `pytube.YouTube(url)` to download the video.
   - Save it to a local path (`~/Downloads/LicensePlateVideos`, for instance).
2. **Local Video Input**:
   - If a user already has a local video, simply reference that path.

### 4.3 Frame Extraction
1. **OpenCV**:
   - Use `cv2.VideoCapture(video_path)` to open the video.
   - Decide on a frame rate or interval for extraction (e.g., every Nth frame or every 1 second).
   - Read frames in a loop until the video ends.

2. **Frame Processing**:
   - Each frame is passed to the detection model for bounding box predictions.
   - Track the current timestamp in seconds or frame index (`frame_count / fps`).

### 4.4 Plate Detection Model
1. **Load the Model**:
   - If using a YOLO-based approach (e.g., YOLOv5, YOLOv8), load it via the relevant library.
2. **Configure Confidence Threshold**:
   - Model’s internal threshold can be set, but also store this threshold in code so it’s easy to adjust later.
3. **Inference**:
   - For each frame, run inference.
   - Retrieve bounding boxes labeled specifically as "license plate" (or the relevant class name).
   - Retrieve confidence scores for these bounding boxes.

### 4.5 OCR and Plate Extraction
1. **Preprocess the License Plate Region**:
   - Crop the bounding box from the frame.
   - Optionally, apply grayscale or thresholding for better OCR results.
2. **Apply OCR**:
   - Use `pytesseract.image_to_string(cropped_frame, config='--psm 7')` (for single text line).
3. **Extract Text**:
   - Clean up the resulting text (remove whitespace, non-alphanumeric chars, etc.).
   - If empty or nonsensical, discard.

### 4.6 Database Storage
1. **Database Schema** (example with SQLite):
   - **Videos** table:
     - `id` (PK)
     - `url` (TEXT)
     - `local_path` (TEXT)
     - `processing_date` (DATETIME)
   - **Plates** table:
     - `id` (PK)
     - `video_id` (FK -> Videos)
     - `timestamp` (REAL or INTEGER representing frame time in seconds)
     - `plate_text` (TEXT)
     - `confidence` (REAL)
     - `bbox` (TEXT or store x1, y1, x2, y2 as separate columns)
2. **Insertion Flow**:
   - When a video is processed, insert a new record in `Videos` if not already present.
   - For each plate detection, insert a row in `Plates`.

### 4.7 Exposing Results
1. **CLI**:
   - For initial usage, a simple command-line interface can display or dump results.
2. **Reporting**:
   - Provide a way (CSV or JSON output) to export all detections for a particular video.

---

## 5. Configuration & Calibration

- **Confidence Threshold**: 
  - A single environment variable or argument (e.g., `--confidence-threshold 0.5`) to filter bounding boxes. 
  - This threshold can also be set within the detection script or passed to the YOLO model at inference time.

- **Frame Skipping**:
  - Another parameter (e.g., `--frame-skip 5`) for how many frames to skip before analyzing the next frame. 
  - This helps reduce computation time if the video is long and plates appear infrequently.

---

## 6. Code Structure

Proposed project directory layout:

```
video_license_plate_tool/
├── README.md
├── requirements.txt
├── main.py
├── detectors/
│   └── yolo_detector.py
├── ocr/
│   └── ocr_utils.py
├── db/
│   ├── models.py
│   └── db_utils.py
├── utils/
│   ├── config.py
│   ├── video_downloader.py
│   └── video_reader.py
└── tests/
    └── test_*.py
```


### 6.1 `main.py`
- **CLI entry point** to run the entire pipeline:
  1. Parse arguments (video URL/path, confidence threshold, frame skip).
  2. Download video if URL is provided.
  3. Initialize database connection.
  4. Call detection pipeline.
  5. Store results.
  6. Print or export summary.

### 6.2 `detectors/yolo_detector.py`
- **`YoloDetector` Class**:
  - Loads YOLO model.
  - Accepts frames, returns bounding boxes + confidence.

### 6.3 `ocr/ocr_utils.py`
- **`extract_text_from_image`** function:
  - Accepts cropped image array.
  - Preprocess image.
  - Calls `pytesseract`.
  - Returns cleaned text.

### 6.4 `db/models.py`
- **SQLAlchemy** or raw SQLite schema definitions:
  - `Video` model
  - `Plate` model

### 6.5 `db/db_utils.py`
- Functions to:
  - Initialize DB.
  - Insert video/plate records.
  - Query results.

### 6.6 `utils/video_downloader.py`
- **`download_video(url)`**:
  - Uses `pytube` or `youtube_dl`.
  - Returns local file path.

### 6.7 `utils/video_reader.py`
- **`process_video(video_path, detector, ocr, db_connection, config)`**:
  - Opens video file with OpenCV.
  - Iterates frames, runs detection, calls OCR, saves to DB if above threshold.

### 6.8 `utils/config.py`
- Store default constants/variables:
  - Default confidence threshold
  - Frame skip
  - DB path
  - Etc.

---

## 7. Performance Considerations

1. **GPU vs CPU**:
   - YOLO or other detection frameworks typically benefit from GPU acceleration. 
   - On macOS, official support for GPU acceleration (e.g., via Metal) might be limited depending on the framework. 
   - If no GPU acceleration is readily available, the Intel Core i9 CPU may suffice but will be slower.
2. **Batch Processing**:
   - If performance becomes an issue, consider batch processing frames for detection.
3. **Model Optimization**:
   - Use half-precision or quantized models for faster inference if the chosen framework supports it.

---

## 8. Deployment & Usage

1. **Local Usage**:
   - Create a Python virtual environment, install the dependencies (`pip install -r requirements.txt`).
   - Run `python main.py --url <VIDEO_URL> --confidence-threshold 0.7 --frame-skip 5`.
2. **Result Checking**:
   - The script prints discovered plates with timestamps.
   - Data is also stored in the SQLite database file, e.g., `license_plate_data.db`.

---

## 9. Future Enhancements

- **Advanced ALPR Libraries**: Instead of generic YOLO + Tesseract, use specialized ALPR frameworks like [OpenALPR](https://www.openalpr.com/) or others that might yield higher accuracy.
- **Web-Based Dashboard**: Provide a front-end to visualize frames, bounding boxes, and search for particular plates across multiple videos.
- **Scaling**: If large-scale usage is needed, containerize the app with Docker, use queue-based processing (e.g., RabbitMQ, Redis), and move to a hosted DB.

---

## 10. Conclusion

This technical specification outlines a robust approach for analyzing YouTube and local video files for visible license plates, extracting their text, and storing these results for future reference. The modular design, configurable thresholds, and straightforward architecture make it suitable for iterative improvement and scaling on macOS systems.
