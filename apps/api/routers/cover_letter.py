"""
Cover letter generation router.
Generates personalized, compelling cover letters using GPT-4o.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Literal
import os
from openai import AsyncOpenAI

router = APIRouter()
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

COVER_LETTER_PROMPT = """Write a concise, genuine cover letter (max 250 words) for this candidate applying to this role.

Guidelines:
- Do NOT use clichés like "I am writing to express my interest" or "I am passionate about"
- Start with a compelling, specific hook that shows you understand the company/role
- Be specific about why THIS company and THIS role appeal to the candidate
- Reference specific achievements or skills from the resume that match the job
- Use the suggested angle provided to frame the letter
- Sign off professionally with the candidate's name
- Write in {tone} tone

Candidate Profile:
{profile_json}

Job Details:
{job_json}

Suggested Angle:
{angle}

Write ONLY the cover letter text. No subject line, no "Dear Hiring Manager" header unless it flows naturally."""


TONE_DESCRIPTIONS = {
    "professional": "formal, polished, and authoritative",
    "enthusiastic": "warm, energetic, and passionate but not sycophantic",
    "concise": "direct, brief, and impactful — every word earns its place",
}


class ProfileData(BaseModel):
    name: str
    summary: Optional[str] = None
    skills: list[str] = []
    experience: list[dict] = []
    education: list[dict] = []


class JobData(BaseModel):
    title: str
    company: str
    description: str
    location: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None


class GenerateCoverLetterRequest(BaseModel):
    profile: ProfileData
    job: JobData
    suggested_angle: Optional[str] = None
    tone: Literal["professional", "enthusiastic", "concise"] = "professional"
    application_id: Optional[str] = None


class GenerateCoverLetterResponse(BaseModel):
    cover_letter: str
    word_count: int
    tone: str
    application_id: Optional[str] = None


@router.post("/generate", response_model=GenerateCoverLetterResponse)
async def generate_cover_letter(request: GenerateCoverLetterRequest):
    """Generate a personalized cover letter using GPT-4o."""
    try:
        import json

        profile_json = json.dumps({
            "name": request.profile.name,
            "summary": request.profile.summary,
            "top_skills": request.profile.skills[:15],
            "recent_experience": request.profile.experience[:3],
            "education": request.profile.education[:2],
        }, indent=2)

        job_json = json.dumps({
            "title": request.job.title,
            "company": request.job.company,
            "location": request.job.location,
            "description": request.job.description[:1500],
        }, indent=2)

        tone_desc = TONE_DESCRIPTIONS.get(request.tone, TONE_DESCRIPTIONS["professional"])

        prompt = COVER_LETTER_PROMPT.format(
            tone=tone_desc,
            profile_json=profile_json,
            job_json=job_json,
            angle=request.suggested_angle or "Highlight the candidate's most relevant experience and genuine interest in this specific role",
        )

        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert career coach and professional writer. Generate cover letters that are authentic, specific, and compelling. Never use generic phrases.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=600,
        )

        cover_letter = response.choices[0].message.content.strip()
        word_count = len(cover_letter.split())

        return GenerateCoverLetterResponse(
            cover_letter=cover_letter,
            word_count=word_count,
            tone=request.tone,
            application_id=request.application_id,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cover letter generation failed: {str(e)}")


@router.post("/regenerate", response_model=GenerateCoverLetterResponse)
async def regenerate_cover_letter(request: GenerateCoverLetterRequest):
    """Regenerate cover letter with different approach (same endpoint, different temperature)."""
    try:
        import json

        profile_json = json.dumps({
            "name": request.profile.name,
            "summary": request.profile.summary,
            "top_skills": request.profile.skills[:15],
            "recent_experience": request.profile.experience[:3],
        }, indent=2)

        job_json = json.dumps({
            "title": request.job.title,
            "company": request.job.company,
            "description": request.job.description[:1500],
        }, indent=2)

        tone_desc = TONE_DESCRIPTIONS.get(request.tone, TONE_DESCRIPTIONS["professional"])

        prompt = COVER_LETTER_PROMPT.format(
            tone=tone_desc,
            profile_json=profile_json,
            job_json=job_json,
            angle=request.suggested_angle or "Try a fresh angle — focus on a specific achievement that demonstrates value",
        )

        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert career coach. Generate a DIFFERENT cover letter than the previous version. Try a completely fresh opening hook and angle.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.9,
            max_tokens=600,
        )

        cover_letter = response.choices[0].message.content.strip()

        return GenerateCoverLetterResponse(
            cover_letter=cover_letter,
            word_count=len(cover_letter.split()),
            tone=request.tone,
            application_id=request.application_id,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cover letter regeneration failed: {str(e)}")
