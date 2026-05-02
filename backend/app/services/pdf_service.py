import io
import json
import base64
from abc import ABC, abstractmethod
from typing import Dict, Any
import fitz
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

    def _pdf_to_base64_image(self, file_content: bytes) -> str:
        try:
            doc = fitz.open(stream=file_content, filetype="pdf")
            page = doc.load_page(0)

            zoom = 2.0
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)

            img_bytes = pix.tobytes("png")
            return base64.b64encode(img_bytes).decode('utf-8')

        except Exception as e:
            raise ValueError(f"Failed to convert PDF file to image: {str(e)}")

    async def _query_ai_with_vision(self, base64_image: str) -> Dict[str, Any]:
        prompt = """
        You are a highly accurate data extraction assistant. 
        Look at the attached image of a Continuing Education (CE) certificate and extract the required fields.
        
        Return ONLY a raw JSON object with the following keys. Do not include markdown formatting (like ```json).
        If a field cannot be found, return null for that field.

        Keys to extract:
        - "provider" (string): The primary company, insurance carrier, or organization issuing the certificate and hosting the course (e.g., 'Equitable Life of Canada', 'iA Financial Group'). Look at the logos at the top/bottom if necessary. Do NOT use accreditation committees or regulatory bodies (like AIC, Alberta Accreditation Committee).
        - "course_name" (string): The title of the course or seminar.
        - "date" (string, format: YYYY-MM-DD): The date the course was completed.
        - "credits" (float): The number of CE credits or hours earned.
        """

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                response_format={ "type": "json_object"},
                messages=[
                    {
                        "role": "user", 
                        "content": [
                            {
                                "type": "text", 
                                "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                temperature=0.1
            )

            content = response.choices[0].message.content.strip()
            return json.loads(content)

        except json.JSONDecodeError:
            raise ValueError("AI failed to return a valid JSON format.")
        except Exception as e:
            raise ValueError(f"OpenAI API request failed: {str(e)}")
    
    async def extract_certificate(self, file_content: bytes) -> Dict[str, Any]:
        base64_image = self._pdf_to_base64_image(file_content)
        structured_data = await self._query_ai_with_vision(base64_image)

        return structured_data