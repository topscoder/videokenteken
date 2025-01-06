# utils/video_downloader.py

import os
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
    stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
    if not stream:
        raise ValueError("No suitable stream found for this video.")
    
    downloaded_file = stream.download(output_path=output_path)
    return downloaded_file
