"""
Recommendation re-ranking router.
Takes top Pinecone candidates and re-ranks using GPT-4o.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import os
import json
import asyncio
from openai import AsyncOpenAI

router = APIRouter()
client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE_URL") or os.getenv("OPENAI_BASE_URL") or None
)
OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "gpt-4o")

RERANK_PROMPT = """You are a job-fit analyzer. Given a candidate's resume summary and a job description, score the fit.

Candidate Resume Summary:
{resume_summary}

Job Description:
Title: {job_title}
Company: {company}
Description: {job_description}

Score the fit from 0-100 across these dimensions:
- skills_match (0-30): Do the candidate's skills match the job requirements?
- experience_level (0-20): Is the candidate's seniority level appropriate for this role?
- domain_relevance (0-20): Is the candidate's industry/domain experience relevant?
- salary_fit (0-15): Does the compensation likely match the candidate's expectations? (assume middle of market if unknown)
- culture_signals (0-15): Do company size and culture signals match the candidate's preferences?

Return ONLY valid JSON with this exact structure:
{
  "total_score": <integer 0-100>,
  "breakdown": {
    "skills_match": <integer 0-30>,
    "experience_level": <integer 0-20>,
    "domain_relevance": <integer 0-20>,
    "salary_fit": <integer 0-15>,
    "culture_signals": <integer 0-15>
  },
  "missing_skills": ["skill1", "skill2"],
  "why_good_fit": "2-3 sentence explanation of why this is a good match",
  "potential_concerns": "1-2 sentence explanation of any concerns or gaps",
  "suggested_angle_for_cover_letter": "1 sentence suggesting the best angle for the cover letter"
}"""


class JobCandidate(BaseModel):
    job_id: str
    title: str
    company: str
    description: str
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    pinecone_score: float = 0.0


class RerankRequest(BaseModel):
    resume_summary: str
    resume_skills: List[str] = []
    candidates: List[JobCandidate]
    top_n: int = 50
    min_score: int = 60


class ScoredJob(BaseModel):
    job_id: str
    total_score: int
    breakdown: dict
    missing_skills: List[str]
    why_good_fit: str
    potential_concerns: str
    suggested_angle_for_cover_letter: str
    pinecone_score: float


class RerankResponse(BaseModel):
    scored_jobs: List[ScoredJob]
    processed: int
    filtered: int


async def score_single_job(
    resume_summary: str, candidate: JobCandidate
) -> Optional[ScoredJob]:
    """Score a single job against the resume using GPT-4o."""
    try:
        prompt = RERANK_PROMPT.format(
            resume_summary=resume_summary[:2000],
            job_title=candidate.title,
            company=candidate.company,
            job_description=candidate.description[:2000],
        )

        response = await client.chat.completions.create(
            model=OPENAI_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a precise job-fit analyzer. Return only valid JSON."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            response_format={"type": "json_object"},
            max_tokens=800,
        )

        data = json.loads(response.choices[0].message.content)

        return ScoredJob(
            job_id=candidate.job_id,
            total_score=data.get("total_score", 0),
            breakdown=data.get("breakdown", {}),
            missing_skills=data.get("missing_skills", []),
            why_good_fit=data.get("why_good_fit", ""),
            potential_concerns=data.get("potential_concerns", ""),
            suggested_angle_for_cover_letter=data.get("suggested_angle_for_cover_letter", ""),
            pinecone_score=candidate.pinecone_score,
        )
    except Exception as e:
        print(f"Error scoring job {candidate.job_id}: {e}")
        return None


@router.post("/rerank", response_model=RerankResponse)
async def rerank_jobs(request: RerankRequest):
    """Re-rank top Pinecone candidates using GPT-4o scoring."""
    # Take top N candidates by Pinecone score for LLM re-ranking
    candidates = sorted(request.candidates, key=lambda x: x.pinecone_score, reverse=True)
    to_process = candidates[:request.top_n]

    # Process concurrently with rate limiting (max 5 concurrent requests)
    semaphore = asyncio.Semaphore(5)

    async def score_with_limit(candidate):
        async with semaphore:
            return await score_single_job(request.resume_summary, candidate)

    results = await asyncio.gather(*[score_with_limit(c) for c in to_process])

    # Filter None results and apply min score
    scored = [r for r in results if r and r.total_score >= request.min_score]
    scored.sort(key=lambda x: x.total_score, reverse=True)

    return RerankResponse(
        scored_jobs=scored,
        processed=len(to_process),
        filtered=len(scored),
    )
