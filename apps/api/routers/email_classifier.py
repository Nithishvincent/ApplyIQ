"""
Email classifier router.
Classifies email content to detect job application status changes.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import os
import json
from openai import AsyncOpenAI

router = APIRouter()
client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE_URL") or os.getenv("OPENAI_BASE_URL") or None
)
OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "gpt-4o")

CLASSIFY_PROMPT = """Analyze this email related to a job application and extract:
1. The application status implied by this email
2. The sentiment (positive/neutral/negative)
3. Any action required from the candidate
4. Key information to extract

Status options: SCREENING, INTERVIEW, OFFER, REJECTED, WITHDRAWN, APPLIED (confirmation), UNKNOWN

Email Subject: {subject}
Email Body: {body}

Return ONLY valid JSON:
{
  "status": "one of the status options above",
  "confidence": <float 0-1>,
  "sentiment": "positive" | "neutral" | "negative",
  "action_required": "string description of what candidate should do, or null",
  "interview_date": "ISO date string if interview scheduled, or null",
  "key_info": "any important extracted info (salary, next steps, etc.)",
  "summary": "1 sentence summary of this email"
}"""

FOLLOWUP_PROMPT = """Write a brief, professional follow-up email (3 sentences max) from {name} checking on the status of their application for {role} at {company}.

Requirements:
- Be warm, not pushy
- Reiterate genuine interest in the specific role
- Ask if there are any updates or next steps
- Do NOT use "I hope this email finds you well" or similar filler
- Sign off with just the candidate's first name

Write ONLY the email body text."""


class ClassifyEmailRequest(BaseModel):
    subject: str
    body: str
    application_id: Optional[str] = None
    gmail_message_id: Optional[str] = None


class ClassifyEmailResponse(BaseModel):
    status: str
    confidence: float
    sentiment: str
    action_required: Optional[str] = None
    interview_date: Optional[str] = None
    key_info: Optional[str] = None
    summary: str
    application_id: Optional[str] = None


class GenerateFollowupRequest(BaseModel):
    name: str
    role: str
    company: str
    applied_date: Optional[str] = None
    application_id: Optional[str] = None


class GenerateFollowupResponse(BaseModel):
    follow_up_email: str
    application_id: Optional[str] = None


@router.post("/classify", response_model=ClassifyEmailResponse)
async def classify_email(request: ClassifyEmailRequest):
    """Classify email content to determine application status change."""
    try:
        prompt = CLASSIFY_PROMPT.format(
            subject=request.subject[:200],
            body=request.body[:3000],
        )

        response = await client.chat.completions.create(
            model=OPENAI_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are an expert at analyzing job application emails. Return only valid JSON."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
            response_format={"type": "json_object"},
            max_tokens=400,
        )

        data = json.loads(response.choices[0].message.content)

        return ClassifyEmailResponse(
            status=data.get("status", "UNKNOWN"),
            confidence=data.get("confidence", 0.0),
            sentiment=data.get("sentiment", "neutral"),
            action_required=data.get("action_required"),
            interview_date=data.get("interview_date"),
            key_info=data.get("key_info"),
            summary=data.get("summary", ""),
            application_id=request.application_id,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email classification failed: {str(e)}")


@router.post("/followup", response_model=GenerateFollowupResponse)
async def generate_followup(request: GenerateFollowupRequest):
    """Generate a follow-up email draft."""
    try:
        prompt = FOLLOWUP_PROMPT.format(
            name=request.name,
            role=request.role,
            company=request.company,
        )

        response = await client.chat.completions.create(
            model=OPENAI_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a professional career coach. Write warm, genuine follow-up emails that are brief and not pushy."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.6,
            max_tokens=200,
        )

        return GenerateFollowupResponse(
            follow_up_email=response.choices[0].message.content.strip(),
            application_id=request.application_id,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Follow-up generation failed: {str(e)}")


@router.post("/batch-classify")
async def batch_classify_emails(requests: List[ClassifyEmailRequest]):
    """Classify multiple emails in parallel."""
    import asyncio

    semaphore = asyncio.Semaphore(5)

    async def classify_with_limit(req):
        async with semaphore:
            try:
                return await classify_email(req)
            except Exception:
                return None

    results = await asyncio.gather(*[classify_with_limit(r) for r in requests[:20]])
    return {"results": [r for r in results if r], "processed": len(results)}
