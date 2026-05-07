from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from app.services.pdf_service import PdfService
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from app.database import engine, get_db, Base, SessionLocal
from app.models import Certificate
import json

load_dotenv()
app = FastAPI()

Base.metadata.create_all(bind=engine)

app.add_middleware(
CORSMiddleware,
# TODO Change origins "*" to Chrome Extension ID in production
allow_origins=["*"], 
allow_credentials=True,
allow_methods=["*"],
allow_headers=["*"],
)

pdf_service = PdfService(openai_api_key=os.getenv("OPENAI_API_KEY"))

async def process_pdf_in_background(content: bytes):
    db = SessionLocal() 

    try:
        data = await pdf_service.extract_certificate(content)
        
        db_cert = Certificate(
            provider=data.get("provider"),
            course_name=data.get("course_name"),
            completion_date=data.get("date"),
            credits=data.get("credits")
        )

        db.add(db_cert)
        db.commit()

    except json.JSONDecodeError:
        print("AI returned invalid JSON format.") # placeholder, update print to use logging module after
    except Exception as e:
        db.rollback()
        print(f"Background task error: {e}")
    finally:
        db.close()

@app.post("/api/v1/extract")
async def extract_certificate(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    content = await file.read()

    background_tasks.add_task(process_pdf_in_background, content)

    return {
        "status": "queued",
        "message": "Certificate received! Processing and saving to database in the background."
    }