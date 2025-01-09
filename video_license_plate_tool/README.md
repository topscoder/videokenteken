# README

## Usage

```shell
usage: main.py [-h] [--video_url VIDEO_URL] [--video_path VIDEO_PATH] [--video_list_file VIDEO_LIST_FILE]
               [--confidence_threshold CONFIDENCE_THRESHOLD] [--frame_skip FRAME_SKIP] [--force] [--skip]

License Plate Detection and OCR from YouTube/Local Videos.

optional arguments:
  -h, --help            show this help message and exit
  --video_url VIDEO_URL
                        URL of a single YouTube video (if you want to download)
  --video_path VIDEO_PATH
                        Local path to a single video file (if already downloaded)
  --video_list_file VIDEO_LIST_FILE
                        Path to text file with multiple video URLs
  --confidence_threshold CONFIDENCE_THRESHOLD
                        Confidence threshold for plate detection (0.0 - 1.0)
  --frame_skip FRAME_SKIP
                        Number of frames to skip between detection attempts
  --force               Force reprocessing without asking if video was processed before
  --skip                Skip reprocessing if video was processed before
```

## Examples

### Process local MP4 video
```shell
python main.py --video_path "../assets/demo.mp4" --confidence_threshold 0.86 --frame_skip 5
```

### Process YouTube video with URL
```shell
python main.py --video_url "https://www.youtube.com/watch?v=VNTl_zhJ9IM" --confidence_threshold 0.86 --frame_skip 5
```

### Force reprocessing videos without asking
```shell
python main.py --video_list_file videos.txt --confidence_threshold 0.5 --frame_skip 5 --force
```

### Skip reprocessing videos without asking
```shell
python main.py --video_list_file videos.txt --confidence_threshold 0.5 --frame_skip 5 --skip
```