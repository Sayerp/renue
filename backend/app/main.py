from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.services.pdf_service import PdfService
import os
from dotenv import load_dotenv

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

@app.post("/api/v1/extract")
async def extract_certificate(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    try:
        content = await file.read()

        data = await pdf_service.extract_certificate(content)

        return {
            "status": "success",
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))