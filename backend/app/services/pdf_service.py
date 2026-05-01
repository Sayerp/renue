import io
import json
from abc import ABC, abstractmethod
from typing import Dict, Any
from pypdf import PdfReader
from openai import AsyncOpenAI

class IPdfService(ABC):
    @abstractmethod
    async def extract_certificate(self, file_content: bytes) -> Dict[str, Any]:
        pass

class PdfService(IPdfService):
    def __init__(self, openai_api_key: str):
        if not openai_api_key:
            raise ValueError("OpenAI API key is missing. Check your .env file.")
    
        self.client = AsyncOpenAI(api_key=openai_api_key)

    def _pdf_to_text(self, file_content: bytes) -> str:
        try:
            pdf_file = io.BytesIO(file_content)
            reader = PdfReader(pdf_file)

            text_pages = []
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_pages.append(page_text)

            full_text = "\n".join(text_pages)

            if len(full_text.strip()) < 10:
                raise ValueError("PDF text is empty or unreadable. It might be a scanned image without OCR.")

            return full_text

        except Exception as e:
            raise ValueError(f"Failed to read PDF file: {str(e)}")

    async def _query_ai_for_json(self, text: str) -> Dict[str, Any]:
        prompt = f"""
        You are a highly accurate data extraction assistant. 
        Analyze the following text from a Continuing Education (CE) certificate and extract the required fields.
        
        Return ONLY a raw JSON object with the following keys. Do not include markdown formatting (like ```json).
        If a field cannot be found, return null for that field.

        Keys to extract:
        - "provider" (string)
        - "course_name" (string)
        - "date" (string, format: YYYY-MM-DD)
        - "credits" (float)

        Text to analyze:
        {text[:3000]}  # Truncate text to save tokens and prevent huge files from breaking the API
        """

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                response_format={ "type": "json_object"}
            )

            content = response.choices[0].message.content.strip()
            return json.loads(content)

        except json.JSONDecodeError:
            raise ValueError("AI failed to return a valid JSON format.")
        except Exception as e:
            raise ValueError(f"OpenAI API request failed: {str(e)}")
    
    async def extract_certificate(self, file_content: bytes) -> Dict[str, Any]:
        raw_text = self._pdf_to_text(file_content)
        structured_data = await self._query_ai_for_json(raw_text)

        return structured_data