"""
Skill gap analysis router.
Analyzes job descriptions to identify missing skills and recommend courses.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
import json
from openai import AsyncOpenAI
from collections import Counter

router = APIRouter()
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SKILL_GAP_PROMPT = """Analyze these job descriptions where the candidate did NOT match well or was rejected.
Extract the top skills, technologies, and qualifications that appear most frequently.

Candidate's existing skills: {candidate_skills}

Job descriptions (partial):
{job_descriptions}

Return ONLY valid JSON:
{
  "missing_skills": [
    {
      "skill": "skill name",
      "frequency": <how many JDs mentioned it>,
      "importance": "high" | "medium" | "low",
      "category": "technical" | "soft" | "domain" | "certification",
      "course_suggestion": "Specific course title to learn this",
      "course_url": "https://... (Coursera, YouTube, or free resource)"
    }
  ],
  "insights": "2-3 sentence actionable insight about the skill gap pattern"
}

Focus on skills the candidate is MISSING (not in their existing skills list).
Sort by frequency descending. Return top 10."""

SCORING_TUNER_PROMPT = """Analyze this outcomes data from a job application process.
Determine which scoring dimensions best predicted interview callbacks vs rejections.

Outcomes data:
{outcomes_json}

Return ONLY valid JSON:
{
  "recommended_weights": {
    "skills_match": <0-30>,
    "experience_level": <0-20>,
    "domain_relevance": <0-20>,
    "salary_fit": <0-15>,
    "culture_signals": <0-15>
  },
  "analysis": "2-3 sentence explanation of what the data shows",
  "top_predictor": "which dimension was most predictive of success"
}"""


class SkillGapRequest(BaseModel):
    user_id: str
    candidate_skills: List[str]
    job_descriptions: List[str]  # List of JD texts that resulted in low scores/rejections


class SkillGapItem(BaseModel):
    skill: str
    frequency: int
    importance: str
    category: str
    course_suggestion: Optional[str] = None
    course_url: Optional[str] = None


class SkillGapResponse(BaseModel):
    missing_skills: List[SkillGapItem]
    insights: str
    user_id: str


class ScoringTunerRequest(BaseModel):
    outcomes: List[dict]  # Each: {job_id, score_breakdown, got_callback, result}


class ScoringTunerResponse(BaseModel):
    recommended_weights: dict
    analysis: str
    top_predictor: str


@router.post("/analyze", response_model=SkillGapResponse)
async def analyze_skill_gap(request: SkillGapRequest):
    """Analyze skill gaps from rejected/low-scoring job applications."""
    if not request.job_descriptions:
        raise HTTPException(status_code=400, detail="No job descriptions provided")

    try:
        # Combine and truncate job descriptions
        combined_jds = "\n\n---\n\n".join(
            [jd[:500] for jd in request.job_descriptions[:20]]
        )

        prompt = SKILL_GAP_PROMPT.format(
            candidate_skills=", ".join(request.candidate_skills[:30]),
            job_descriptions=combined_jds[:6000],
        )

        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a career development expert. Identify actionable skill gaps with specific learning resources."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            response_format={"type": "json_object"},
            max_tokens=1500,
        )

        data = json.loads(response.choices[0].message.content)
        missing_skills = [SkillGapItem(**s) for s in data.get("missing_skills", [])]

        return SkillGapResponse(
            missing_skills=missing_skills,
            insights=data.get("insights", ""),
            user_id=request.user_id,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Skill gap analysis failed: {str(e)}")


@router.post("/tune-scoring", response_model=ScoringTunerResponse)
async def tune_scoring(request: ScoringTunerRequest):
    """Re-weight scoring formula based on historical outcomes."""
    if len(request.outcomes) < 5:
        raise HTTPException(status_code=400, detail="Need at least 5 outcomes to tune scoring")

    try:
        prompt = SCORING_TUNER_PROMPT.format(
            outcomes_json=json.dumps(request.outcomes[:50], indent=2)[:4000]
        )

        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a data scientist analyzing job application success patterns. Return only valid JSON."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            response_format={"type": "json_object"},
            max_tokens=500,
        )

        data = json.loads(response.choices[0].message.content)

        return ScoringTunerResponse(
            recommended_weights=data.get("recommended_weights", {}),
            analysis=data.get("analysis", ""),
            top_predictor=data.get("top_predictor", ""),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scoring tuning failed: {str(e)}")
