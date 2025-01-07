#!/usr/bin/env python3
"""
A simple Flask-based web UI to search for license plates in our SQLite database
and link to the relevant YouTube timestamps.
"""

from flask import Flask, request, render_template
from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker
from db.models import Base, Video, Plate
import os
import re

app = Flask(__name__)

# Adjust this path if your main DB file is in a different location
DB_PATH = os.path.join(os.getcwd(), "license_plate_data.db")

def get_db_session():
    engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

@app.route("/", methods=["GET"])
def home():
    """
    Display a simple search form.
    """
    return render_template("search.html")

@app.route("/videos", methods=["GET"])
def videos():
    """
    Display a list of videos in the database.
    """
    session = get_db_session()
    videos = session.query(Video).all()
    session.close()
    return render_template("videos.html", videos=videos)

@app.route("/plates", methods=["GET"])
def plates():
    """
    Display a list of plates in the database, grouped by plate_text and ordered ascending.
    Only show each found plate_text once.
    """
    session = get_db_session()
    results = session.query(Plate).all()
     # Build a small list of search result dicts with the data we need
    output_results = []
    for plate in results:
        video = plate.video  # relationship from Plate to Video
        # Convert the plate text to uppercase
        plate_text_upper = plate.plate_text.upper() if plate.plate_text else ""

        # Build a direct YouTube link with a timestamp
        # 1) Attempt to parse the YouTube video ID from the url if it's in typical format (e.g., ?v=VIDEO_ID)
        # 2) If we find it, use https://youtu.be/VIDEO_ID?t=TIMESTAMP
        # 3) Otherwise, fall back to appending &t=TIMESTAMP or use the raw URL

        video_url = video.url or ""
        timestamp_sec = int(plate.timestamp)  # convert float -> int for link

        # Regex to find "v=xxxx" in the original URL
        youtube_id_matches = re.findall(r"v=([^&]+)", video_url)
        if youtube_id_matches:
            youtube_id = youtube_id_matches[0]
            # build shortened link
            direct_link = f"https://youtu.be/{youtube_id}?t={timestamp_sec}"
        else:
            # fallback approach, just append ?t=timestamp
            # works if the video_url is a standard youtube.com/watch?v=VIDEO_ID
            if "?" in video_url:
                direct_link = f"{video_url}&t={timestamp_sec}"
            else:
                direct_link = f"{video_url}?t={timestamp_sec}"

        output_results.append({
            "plate_text": plate_text_upper,
            "timestamp": plate.timestamp,
            "video_link": direct_link,
        })

    session.close()
    return render_template("plates.html", plates=output_results)

@app.route("/search", methods=["POST"])
def search():
    """
    Process the search request for a license plate string.
    Perform a case-insensitive partial match on the Plate.plate_text field.
    """
    plate_query = request.form.get("license_plate", "").strip()
    if not plate_query:
        return render_template("search.html", error="Please enter a license plate to search.")

    session = get_db_session()

    # We do a partial, case-insensitive match (SQLite uses case-insensitive for LIKE by default)
    # Alternatively, you can do: Plate.plate_text.ilike(f'%{plate_query}%') with PostgreSQL, etc.
    results = (
        session.query(Plate)
        .join(Video, Plate.video_id == Video.id)
        .filter(Plate.plate_text.like(f"%{plate_query}%"))
        .all()
    )

    # Build a small list of search result dicts with the data we need
    output_results = []
    for plate in results:
        video = plate.video  # relationship from Plate to Video
        # Convert the plate text to uppercase
        plate_text_upper = plate.plate_text.upper() if plate.plate_text else ""

        # Build a direct YouTube link with a timestamp
        # 1) Attempt to parse the YouTube video ID from the url if it's in typical format (e.g., ?v=VIDEO_ID)
        # 2) If we find it, use https://youtu.be/VIDEO_ID?t=TIMESTAMP
        # 3) Otherwise, fall back to appending &t=TIMESTAMP or use the raw URL

        video_url = video.url or ""
        timestamp_sec = int(plate.timestamp)  # convert float -> int for link

        # Regex to find "v=xxxx" in the original URL
        youtube_id_matches = re.findall(r"v=([^&]+)", video_url)
        if youtube_id_matches:
            youtube_id = youtube_id_matches[0]
            # build shortened link
            direct_link = f"https://youtu.be/{youtube_id}?t={timestamp_sec}"
        else:
            # fallback approach, just append ?t=timestamp
            # works if the video_url is a standard youtube.com/watch?v=VIDEO_ID
            if "?" in video_url:
                direct_link = f"{video_url}&t={timestamp_sec}"
            else:
                direct_link = f"{video_url}?t={timestamp_sec}"

        output_results.append({
            "plate_text": plate_text_upper,
            "timestamp": plate.timestamp,
            "video_link": direct_link,
        })

    session.close()

    # Render results
    return render_template("results.html", query=plate_query, results=output_results)

if __name__ == "__main__":
    # Run the Flask dev server
    app.run(debug=True, host="127.0.0.1", port=5000)
