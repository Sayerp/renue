from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.services.pdf_service import PdfService
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from app.database import engine, get_db, Base
from app.models import Certificate

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

@app.post("/api/v1/extract")
async def extract_certificate(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    try:
        content = await file.read()

        data = await pdf_service.extract_certificate(content)

        db_cert = Certificate(
            provider = data.get("provider"),
            course_name = data.get("course_name"),
            completion_date = data.get("date"),
            credits = data.get("credits")
        )

        db.add(db_cert)
        db.commit()
        db.refresh(db_cert)

        return {
            "status": "success",
            "data": data,
            "db_id": str(db_cert.id)
        }
    
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="AI returned invalid JSON format.")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))