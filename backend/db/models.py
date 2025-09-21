from sqlalchemy import Column, String, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(String, primary_key=True)
    status = Column(String, default="uploaded")  # uploaded, processing, ocr_done, llm_done, lesson_built, completed, error
    created_at = Column(DateTime, default=datetime.utcnow)
    error_message = Column(Text, nullable=True)
    lesson_id = Column(String, nullable=True)
    
    # Relationships
    images = relationship("Image", back_populates="job")

class Image(Base):
    __tablename__ = "images"
    
    id = Column(String, primary_key=True)
    job_id = Column(String, ForeignKey("jobs.id"))
    filename = Column(String)
    file_path = Column(String)
    tag = Column(String, nullable=True)  # pic1, pic2, etc.
    ocr_result = Column(Text, nullable=True)
    processed_at = Column(DateTime, nullable=True)
    
    # Relationships
    job = relationship("Job", back_populates="images")

class Lesson(Base):
    __tablename__ = "lessons"
    
    id = Column(String, primary_key=True)
    job_id = Column(String, ForeignKey("jobs.id"))
    title = Column(String)
    steps = Column(JSON)  # Structured lesson data
    created_at = Column(DateTime, default=datetime.utcnow)

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
