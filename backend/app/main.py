from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from app.services.pdf_service import PdfService
import os
import uuid
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from app.database import get_db, SessionLocal
from app.models import Certificate, ExtractionJob
from app.auth import get_current_user_id

load_dotenv()
app = FastAPI()

app.add_middleware(
CORSMiddleware,
# TODO Change origins "*" to Chrome Extension ID in production
allow_origins=["*"],
allow_credentials=True,
allow_methods=["*"],
allow_headers=["*"],
)

pdf_service = PdfService(openai_api_key=os.getenv("OPENAI_API_KEY"))

async def process_pdf_in_background(job_id: uuid.UUID, user_id: uuid.UUID, content: bytes):
    db = SessionLocal()

    try:
        data = await pdf_service.extract_certificate(content)

        db_cert = Certificate(
            user_id=user_id,
            provider=data.get("provider"),
            course_name=data.get("course_name"),
            completion_date=data.get("date"),
            credits=data.get("credits")
        )

        db.add(db_cert)
        db.flush()

        job = db.get(ExtractionJob, job_id)
        job.status = "completed"
        job.certificate_id = db_cert.id
        db.commit()

    except Exception as e:
        db.rollback()
        job = db.get(ExtractionJob, job_id)
        job.status = "failed"
        job.error_message = str(e)
        db.commit()
    finally:
        db.close()

@app.post("/api/v1/extract")
async def extract_certificate(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    content = await file.read()
    user_id = uuid.UUID(user_id)

    job = ExtractionJob(user_id=user_id, status="processing")
    db.add(job)
    db.commit()
    db.refresh(job)

    background_tasks.add_task(process_pdf_in_background, job.id, user_id, content)

    return {"job_id": job.id, "status": job.status}
