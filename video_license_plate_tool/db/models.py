# db/models.py

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship, validates

Base = declarative_base()

class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String, nullable=True)
    local_path = Column(String, nullable=True)
    processing_date = Column(DateTime, nullable=True)

    plates = relationship("Plate", back_populates="video")

class Plate(Base):
    __tablename__ = "plates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    video_id = Column(Integer, ForeignKey("videos.id"), nullable=False)
    timestamp = Column(Float, nullable=False)
    plate_text = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)
    bbox = Column(Text, nullable=True)

    video = relationship("Video", back_populates="plates")

    @validates('plate_text')
    def convert_upper(self, key, value):
        return value.upper()