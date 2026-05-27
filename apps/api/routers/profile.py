"""
Resume parsing router.
Accepts raw resume text → GPT-4o → structured JSON profile.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import os
import json
from openai import AsyncOpenAI

router = APIRouter()
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

RESUME_PARSE_PROMPT = """Extract the following fields from this resume into JSON.
Be thorough — extract all information available. Use null for missing fields.

Required JSON structure:
{
  "name": "string",
  "email": "string or null",
  "phone": "string or null",
  "location": "string or null",
  "summary": "string or null",
  "skills": ["skill1", "skill2", ...],
  "experience": [
    {
      "title": "string",
      "company": "string",
      "location": "string or null",
      "start": "YYYY-MM or Month YYYY",
      "end": "YYYY-MM or Month YYYY or Present",
      "bullets": ["bullet1", "bullet2", ...]
    }
  ],
  "education": [
    {
      "degree": "string",
      "field": "string or null",
      "institution": "string",
      "year": "YYYY or null",
      "gpa": "string or null"
    }
  ],
  "certifications": ["cert1", "cert2", ...],
  "languages": ["language1", "language2", ...],
  "projects": [
    {
      "name": "string",
      "description": "string or null",
      "technologies": ["tech1", ...]
    }
  ],
  "links": {
    "linkedin": "string or null",
    "github": "string or null",
    "portfolio": "string or null"
  }
}

Resume text:
"""


class ParseResumeRequest(BaseModel):
    resume_text: str
    user_id: Optional[str] = None


class ParseResumeResponse(BaseModel):
    parsed: dict
    raw_text: str
    token_count: Optional[int] = None


@router.post("/parse", response_model=ParseResumeResponse)
async def parse_resume(request: ParseResumeRequest):
    """Parse resume text into structured JSON using GPT-4o."""
    if not request.resume_text or len(request.resume_text.strip()) < 50:
        raise HTTPException(status_code=400, detail="Resume text too short or empty")

    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert resume parser. Extract structured data from resumes. Always return valid JSON only, no markdown formatting, no code blocks.",
                },
                {
                    "role": "user",
                    "content": RESUME_PARSE_PROMPT + request.resume_text[:8000],
                },
            ],
            temperature=0.1,
            response_format={"type": "json_object"},
            max_tokens=4000,
        )

        raw_json = response.choices[0].message.content
        parsed = json.loads(raw_json)

        return ParseResumeResponse(
            parsed=parsed,
            raw_text=request.resume_text,
            token_count=response.usage.total_tokens if response.usage else None,
        )

    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse GPT response as JSON: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Resume parsing failed: {str(e)}")
