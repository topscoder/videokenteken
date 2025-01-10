# README

## Usage

```shell
usage: main.py [-h] [--video_url VIDEO_URL] [--video_path VIDEO_PATH] [--video_list_file VIDEO_LIST_FILE] [--playlist_url PLAYLIST_URL] [--channel_url CHANNEL_URL] [--confidence_threshold CONFIDENCE_THRESHOLD] [--frame_skip FRAME_SKIP] [--force]

License Plate Detection and OCR from YouTube/Local Videos.

optional arguments:
  -h, --help            show this help message and exit
  --video_url VIDEO_URL
                        URL of a single YouTube video
  --video_path VIDEO_PATH
                        Local path to a single video file
  --video_list_file VIDEO_LIST_FILE
                        Path to text file with multiple video URLs
  --playlist_url PLAYLIST_URL
                        URL of a YouTube playlist
  --channel_url CHANNEL_URL
                        URL of a YouTube channel
  --confidence_threshold CONFIDENCE_THRESHOLD
                        Confidence threshold for plate detection (0.0 - 1.0)
  --frame_skip FRAME_SKIP
                        Number of frames to skip between detection attempts
  --force               Force reprocessing without asking if video was processed before
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

## YouTube Channels

* De Car Guys https://www.youtube.com/@decarguys
* Gumbal  https://www.youtube.com/@Gumbal
* Autoblog  https://www.youtube.com/@Autoblog
* AutoWeek  https://www.youtube.com/@AutoWeek
* ANWB      https://www.youtube.com/@ANWB
* Autovisie https://www.youtube.com/@autovisie
* DriversDream  https://www.youtube.com/@DriversDreamNL
* EP Autoimport   https://www.youtube.com/@EPautoimport
* Twins.TV  https://www.youtube.com/@Twins.TV_
* RJTDBF   https://www.youtube.com/channel/UCz-QchirkydlNGbbc8K59Xw
* Autobedrijf John van der Rijt   https://www.youtube.com/@AutobedrijfJohnvanderRijt
* EmreDrives  https://www.youtube.com/@EmreDrives
* AutoRAI TV  https://www.youtube.com/@AutoRAITV
* Stipt Polish Point  https://www.youtube.com/@StiptPolishPoint
* Vierenzestig Porsche Portal https://www.youtube.com/@vierenzestig
* DutchRiders https://www.youtube.com/@DutchRiders1
* AutoTopNL https://www.youtube.com/@AutoTopNL
* Werner Budding https://www.youtube.com/@WernerBudding
* cvdzijden - Supercar Videos https://www.youtube.com/@cvdzijden
* CarSpotterQVS   https://www.youtube.com/channel/UCnw5r8QG5VoaYRjI4_3Sd1Q
* Lars Mars Cars  https://www.youtube.com/@LarsMarsCars
* Dutch Motorsport  https://www.youtube.com/@DutchMotorsport
* Sem Meijer  https://www.youtube.com/channel/UCgPwPqzvzDgKSq-DhcZS11Q
* JvDSupercars  https://www.youtube.com/channel/UCMxbeeKNk42Jv33WbvpGMyQ
* 112NoordWestNL  https://www.youtube.com/channel/UCe9L_7nQEO7j5QDjzEO_-Ew