# db/db_utils.py

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base, Video, Plate
from datetime import datetime

def init_db(db_path):
    """
    Initialize (and create if not exists) the SQLite database.
    :param db_path: Path to the SQLite database file.
    :return: session
    """
    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    # Create all tables if they don't exist
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

def insert_video_record(session, url, local_path, processing_date):
    """
    Insert a video record. If it already exists, returns the existing record's ID.
    :param session: db session
    :param url: str
    :param local_path: str
    :param processing_date: datetime
    :return: int (video_id)
    """
    video = Video(url=url, local_path=local_path, processing_date=processing_date)
    session.add(video)
    session.commit()
    return video.id

def insert_plate_record(session, video_id, timestamp, plate_text, confidence, bbox):
    """
    Insert a new plate record.
    :param session: db session
    :param video_id: int
    :param timestamp: float
    :param plate_text: str
    :param confidence: float
    :param bbox: str (json or textual representation)
    """
    plate = Plate(
        video_id=video_id,
        timestamp=timestamp,
        plate_text=plate_text,
        confidence=confidence,
        bbox=bbox
    )
    session.add(plate)
    session.commit()
