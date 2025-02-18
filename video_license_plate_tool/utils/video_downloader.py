# utils/video_downloader.py

import os
import re
# from pytube import YouTube
from pytubefix import YouTube

def download_video(url, output_path=None):
    """
    Download a YouTube video to the specified path or current directory.
    :param url: str, YouTube video link
    :param output_path: str, directory to save video
    :return: str, local video file path
    """
    if output_path is None:
        output_path = os.getcwd()

    yt = YouTube(url)
    stream = yt.streams.get_highest_resolution()
    if not stream:
        raise ValueError("No suitable stream found for this video.")
    
    # Use a regex to extract the video ID from the URL
    target_filename = None
    match = re.search(r"v=([^&]+)", yt.watch_url)
    if match:
        video_id = match.group(1)
        target_filename = video_id + ".mp4"
        
    downloaded_file = stream.download(output_path=output_path, filename=target_filename)
    return downloaded_file
