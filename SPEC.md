# Technical Specification: Enhanced Video License Plate Analysis Tool

## 1. Overview

This tool analyzes video files (primarily YouTube videos) to detect visible license plates, extract their text via OCR, store the results in a database, and provide a search interface to retrieve information based on license plate queries. The system has been enhanced with features to:

- Measure and report processing time and video duration.
- Check for previously analyzed videos and prompt for reprocessing or force processing.
- Process multiple videos in batch using various sources:
  - A list of video URLs from a text file.
  - All videos from a YouTube playlist.
  - All videos from a YouTube channel.
- Account for OCR misreads by handling similar characters during license plate search queries.

---

## 2. Requirements

1. **Operating System**: macOS (Intel Core i9 CPU) or Raspberry Pi 4.
2. **Primary Language**: Python 3.8+.
3. **Libraries & Tools**:
   - Video processing: OpenCV, FFmpeg.
   - Object detection: Ultralytics YOLO (e.g., YOLOv8).
   - OCR: Tesseract, PyTesseract.
   - YouTube downloading and data extraction: Pytube.
   - Database: SQLite, SQLAlchemy.
   - Web framework: Flask (for the search UI).
4. **Additional Python Packages**: 
   - Standard libraries: `argparse`, `datetime`, `itertools`, etc.
   - Other dependencies as required for similarity mapping and YouTube playlist/channel handling.

---

## 3. Architecture & Flow

### 3.1 High-Level Workflow

1. **Video Acquisition**:
   - Accepts single video URLs/paths, a text file with multiple video URLs, a YouTube playlist URL, or a YouTube channel URL.
   - Downloads videos from YouTube as necessary.

2. **Pre-Processing Checks**:
   - Checks the database for prior processing of the video(s).
   - If a video has been processed before, prompts the user to decide whether to reprocess or uses a force flag to bypass the prompt.

3. **Video Processing**:
   - Processes each video using YOLO for license plate detection and OCR for text extraction.
   - Measures the total processing time for each video.
   - Calculates and reports the total duration of the video.

4. **Database Storage**:
   - Stores video metadata, timestamps, detected license plate texts, confidence scores, and bounding box coordinates.

5. **Search Interface**:
   - Provides a web-based UI with Flask for searching license plates.
   - Implements character similarity mapping to account for OCR misreads in search queries.
   - Lists search results with uppercase license plates and links to YouTube timestamps.

---

## 4. Detailed Implementation Steps

### 4.1 Environment Setup
- Install Python 3.8+ and required libraries as previously detailed.
- Configure Tesseract and YOLO model paths.
- Ensure the database schema is set up using SQLAlchemy models.

### 4.2 Video Processing Enhancements

#### Command-Line Options
- `--video_url`: URL of a single YouTube video.
- `--video_path`: Local path to a single video file.
- `--video_list_file`: Path to a text file with multiple video URLs.
- `--playlist_url`: URL of a YouTube playlist to process all videos from.
- `--channel_url`: URL of a YouTube channel to process all videos from.
- `--confidence_threshold`: Confidence threshold for license plate detection.
- `--frame_skip`: Number of frames to skip between detection attempts.
- `--force`: Force reprocessing without prompting if the video was analyzed before.

#### Main Script (`main.py`)
- **Initialization**:
  - Parse arguments, including new options for playlists and channels.
  - Validate input ensuring at least one video source is provided.
  - Initialize a single database session for processing.

- **Source Handling**:
  - If `--video_list_file` is provided, read video URLs from the file.
  - If `--playlist_url` is provided, use `pytube.Playlist` to retrieve all video URLs from the playlist.
  - If `--channel_url` is provided, use `pytube.Channel` to retrieve all video URLs from the channel.
  - Aggregate all collected URLs into a list for batch processing.

- **Processing Single Video**:
  - Encapsulate logic in a `process_single_video()` function, handling downloading, database checks, and video analysis as previously specified.
  - For each video URL in the aggregated list, call `process_single_video()` with appropriate parameters.

- **Measurement and Reporting**:
  - For each video, record start and end times, calculate total processing time, and determine video duration.
  - Print out processing metrics for user information.

### 4.3 Database Schema & Utilities
- Use existing `Video` and `Plate` models.
- `db_utils` should provide functions for:
  - Database initialization (`init_db`).
  - Inserting video and plate records.
  - Querying for existing videos.

### 4.4 Web UI Search Enhancements
- **Similarity Mapping**:  
  Create a similarity map for characters frequently confused by OCR.

  ```python
  similar_map = {
      '8': ['8', 'B'],
      'B': ['B', '8'],
      '1': ['1', 'I', 'L'],
      'I': ['I', '1', 'L'],
      'L': ['L', '1', 'I'],
      '0': ['0', 'O'],
      'O': ['O', '0'],
      # Add additional mappings as needed
  }
- **Pattern Generation**:
   Implement a function generate_patterns(query, similar_map) that creates all plausible variants of the search query by substituting characters based on the similarity map.
- **Search Query Modification**:
   Modify the search function to:
   * Generate patterns based on the user input.
   * Build a SQLAlchemy query using OR conditions to match any of the generated patterns with .like() filters.
- **Web UI Flow**:
   * User enters a license plate (e.g., "X120BF").
   * Application generates variants (e.g., "X120BF", "X1208F", etc.).
   * Searches database and lists all matching entries.
   * Each result shows the license plate in uppercase and provides a clickable link to the YouTube video at the timestamp where the plate was detected.

### 5. Code Structure
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
│   ├── __init__.py
│   ├── models.py
│   └── db_utils.py
├── utils/
│   ├── config.py
│   ├── video_downloader.py
│   └── video_reader.py
├── webui/
│   ├── app.py
│   ├── requirements.txt
│   └── templates/
│       ├── layout.html
│       ├── search.html
│       └── results.html
└── tests/
    └── test_*.py
```

* `main.py`:
Updated to handle multiple video sources including playlists and channels, force reprocessing, measure processing time, calculate video duration, and prompt user on reprocessing.

* Database (`db/`):
Used for storing and querying video processing records.

* Web UI (`webui/`):
Provides a search interface with enhanced search capability to handle OCR misreads.

### 6. Additional Considerations

- **Performance Optimization**:
Care must be taken when generating search patterns for long queries with many ambiguous characters, as the number of combinations can grow quickly.

- **Error Handling**:
Implement robust error handling for network issues (e.g., fetching playlist/channel videos), file I/O, video download failures, and database operations.

- **Scalability & Extensibility**:
The architecture supports batch processing from various sources and can be extended with more advanced search algorithms or additional video sources.

### 7. Conclusion

This updated specification incorporates new functionalities to process videos from YouTube playlists and channels in addition to previous features. It maintains a consistent command-line interface and modular design, ensuring a logical user experience and scalable architecture. The enhanced search accommodates OCR errors, and the system now supports batch processing from multiple video sources with detailed reporting and control over reprocessing.