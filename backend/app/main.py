from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from app.services.pdf_service import PdfService
from pydantic import BaseModel
from typing import Optional
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

class CertificateUpdate(BaseModel):
    provider: Optional[str] = None
    course_name: Optional[str] = None
    completion_date: Optional[str] = None
    credits: Optional[float] = None

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

@app.get("/api/v1/jobs/{job_id}")
async def get_job_status(job_id: uuid.UUID, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    user_id = uuid.UUID(user_id)
    job = db.get(ExtractionJob, job_id)

    if not job or job.user_id != user_id:
        raise HTTPException(status_code=404, detail="Job not found.")

    response = {"job_id": job.id, "status": job.status}

    if job.status == "completed":
        certificate = db.get(Certificate, job.certificate_id)
        response["certificate"] = {
            "id": certificate.id,
            "provider": certificate.provider,
            "course_name": certificate.course_name,
            "completion_date": certificate.completion_date,
            "credits": certificate.credits,
        }
    elif job.status == "failed":
        response["error"] = job.error_message

    return response

@app.get("/api/v1/certificates")
async def list_certificates(user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    user_id = uuid.UUID(user_id)
    certificates = db.query(Certificate).filter(Certificate.user_id == user_id).all()

    return [
        {
            "id": cert.id,
            "provider": cert.provider,
            "course_name": cert.course_name,
            "completion_date": cert.completion_date,
            "credits": cert.credits,
        }
        for cert in certificates
    ]

@app.patch("/api/v1/certificates/{certificate_id}")
async def update_certificate(
    certificate_id: uuid.UUID,
    updates: CertificateUpdate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    user_id = uuid.UUID(user_id)
    certificate = db.get(Certificate, certificate_id)

    if not certificate or certificate.user_id != user_id:
        raise HTTPException(status_code=404, detail="Certificate not found.")

    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(certificate, field, value)

    db.commit()
    db.refresh(certificate)

    return {
        "id": certificate.id,
        "provider": certificate.provider,
        "course_name": certificate.course_name,
        "completion_date": certificate.completion_date,
        "credits": certificate.credits,
    }
