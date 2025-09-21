from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
import os
import uuid
import shutil
from datetime import datetime

from db.database import engine, get_db
from db.models import Base, Job, Lesson, Image
from services.ocr_service import OCRService
from services.llm_service import LLMService
from services.sympy_service import SymPyService
from services.lesson_builder import LessonBuilder
from sqlalchemy.orm import Session

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Math Scrap to Lesson API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure upload directory exists
os.makedirs("uploads", exist_ok=True)

# Initialize services
ocr_service = OCRService()
llm_service = LLMService()
sympy_service = SymPyService()
lesson_builder = LessonBuilder(ocr_service, llm_service, sympy_service)

@app.get("/")
async def root():
    return {"message": "Math Scrap to Lesson API", "version": "1.0.0"}

@app.post("/upload")
async def upload_images(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    tags: Optional[str] = None
):
    """Upload images and start processing pipeline"""
    
    # Generate job ID
    job_id = str(uuid.uuid4())
    
    # Create job in database
    db = next(get_db())
    job = Job(
        id=job_id,
        status="uploaded",
        created_at=datetime.utcnow()
    )
    db.add(job)
    db.commit()
    
    # Save uploaded files
    file_paths = []
    for i, file in enumerate(files):
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail=f"File {file.filename} is not an image")
        
        # Generate unique filename
        file_extension = file.filename.split('.')[-1]
        filename = f"{job_id}_{i}.{file_extension}"
        file_path = f"uploads/{filename}"
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        file_paths.append(file_path)
        
        # Create image record
        image = Image(
            id=str(uuid.uuid4()),
            job_id=job_id,
            filename=filename,
            file_path=file_path,
            tag=tags.split(',')[i] if tags and i < len(tags.split(',')) else None
        )
        db.add(image)
    
    db.commit()
    db.close()
    
    # Start background processing
    background_tasks.add_task(process_images, job_id, file_paths)
    
    return {"job_id": job_id, "message": "Upload successful, processing started"}

@app.get("/status/{job_id}")
async def get_job_status(job_id: str):
    """Get processing status for a job"""
    db = next(get_db())
    job = db.query(Job).filter(Job.id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    response = {
        "job_id": job_id,
        "status": job.status,
        "created_at": job.created_at,
        "ocr_done": job.status in ["ocr_done", "llm_done", "lesson_built", "completed"],
        "llm_done": job.status in ["llm_done", "lesson_built", "completed"],
        "lesson_built": job.status in ["lesson_built", "completed"],
        "lesson_id": job.lesson_id if job.lesson_id else None
    }
    
    if job.error_message:
        response["error"] = job.error_message
    
    db.close()
    return response

@app.get("/lesson/{lesson_id}")
async def get_lesson(lesson_id: str):
    """Get structured lesson data"""
    db = next(get_db())
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    response = {
        "lesson_id": lesson_id,
        "title": lesson.title,
        "steps": lesson.steps,
        "created_at": lesson.created_at,
        "job_id": lesson.job_id
    }
    
    db.close()
    return response

async def process_images(job_id: str, file_paths: List[str]):
    """Background task to process uploaded images"""
    db = next(get_db())
    
    try:
        # Update job status
        job = db.query(Job).filter(Job.id == job_id).first()
        job.status = "processing"
        db.commit()
        
        # Build lesson from images
        lesson_data = await lesson_builder.build_lesson(job_id, file_paths)
        
        # Create lesson record
        lesson = Lesson(
            id=str(uuid.uuid4()),
            job_id=job_id,
            title=lesson_data["title"],
            steps=lesson_data["steps"]
        )
        db.add(lesson)
        
        # Update job with lesson ID
        job.lesson_id = lesson.id
        job.status = "completed"
        db.commit()
        
    except Exception as e:
        # Update job with error
        job = db.query(Job).filter(Job.id == job_id).first()
        job.status = "error"
        job.error_message = str(e)
        db.commit()
    
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
