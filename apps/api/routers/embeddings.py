"""
Embeddings router.
Generates text embeddings using OpenAI text-embedding-3-small
and upserts them to Pinecone.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import os
from openai import AsyncOpenAI
from pinecone import Pinecone, ServerlessSpec

router = APIRouter()
openai_client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE_URL") or os.getenv("OPENAI_BASE_URL") or None
)
OPENAI_EMBEDDING_MODEL_NAME = os.getenv("OPENAI_EMBEDDING_MODEL_NAME", "text-embedding-3-small")

# Lazy Pinecone initialization
_pc: Optional[Pinecone] = None
_index = None


def get_pinecone_index():
    global _pc, _index
    if _index is None:
        _pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        index_name = os.getenv("PINECONE_INDEX_NAME", "applyiq-jobs")

        # Create index if it doesn't exist
        existing = [i.name for i in _pc.list_indexes()]
        if index_name not in existing:
            _pc.create_index(
                name=index_name,
                dimension=int(os.getenv("EMBEDDING_DIMENSION", "1536")),  # configurable dimension
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region=os.getenv("PINECONE_ENVIRONMENT", "us-east-1"),
                ),
            )
        _index = _pc.Index(index_name)
    return _index


async def embed_text(text: str) -> List[float]:
    """Generate embedding for a single text string."""
    response = await openai_client.embeddings.create(
        model=OPENAI_EMBEDDING_MODEL_NAME,
        input=text[:8000],  # token limit safety
    )
    return response.data[0].embedding


class EmbedJobRequest(BaseModel):
    job_id: str
    title: str
    company: str
    description: str
    location: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    source: Optional[str] = None
    work_mode: Optional[str] = None


class EmbedJobResponse(BaseModel):
    job_id: str
    embedding_id: str
    success: bool


class EmbedResumeRequest(BaseModel):
    user_id: str
    resume_text: str


class EmbedResumeResponse(BaseModel):
    user_id: str
    embedding: List[float]
    dimension: int


class SearchJobsRequest(BaseModel):
    resume_text: str
    top_k: int = 200
    score_min: float = 0.0
    filters: Optional[dict] = None


class SearchJobsResponse(BaseModel):
    matches: List[dict]
    count: int


@router.post("/job", response_model=EmbedJobResponse)
async def embed_job(request: EmbedJobRequest):
    """Embed a job and upsert to Pinecone."""
    try:
        # Compose text: title + company + first 500 chars of description
        embed_text_content = (
            f"{request.title} at {request.company}. "
            f"{request.description[:500]}"
        )

        embedding = await embed_text(embed_text_content)
        embedding_id = f"job_{request.job_id}"

        index = get_pinecone_index()
        index.upsert(
            vectors=[
                {
                    "id": embedding_id,
                    "values": embedding,
                    "metadata": {
                        "job_id": request.job_id,
                        "title": request.title,
                        "company": request.company,
                        "location": request.location or "",
                        "source": request.source or "",
                        "work_mode": request.work_mode or "",
                        "salary_min": request.salary_min or 0,
                        "salary_max": request.salary_max or 0,
                    },
                }
            ],
            namespace="jobs",
        )

        return EmbedJobResponse(
            job_id=request.job_id,
            embedding_id=embedding_id,
            success=True,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding failed: {str(e)}")


@router.post("/resume", response_model=EmbedResumeResponse)
async def embed_resume(request: EmbedResumeRequest):
    """Generate embedding for a user's resume (not stored in Pinecone)."""
    try:
        embedding = await embed_text(request.resume_text)
        return EmbedResumeResponse(
            user_id=request.user_id,
            embedding=embedding,
            dimension=len(embedding),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Resume embedding failed: {str(e)}")


@router.post("/search", response_model=SearchJobsResponse)
async def search_jobs(request: SearchJobsRequest):
    """Search Pinecone for jobs similar to the resume."""
    try:
        resume_embedding = await embed_text(request.resume_text)
        index = get_pinecone_index()

        query_params = {
            "vector": resume_embedding,
            "top_k": request.top_k,
            "namespace": "jobs",
            "include_metadata": True,
        }

        results = index.query(**query_params)

        matches = []
        for match in results.matches:
            if match.score >= request.score_min:
                matches.append({
                    "embedding_id": match.id,
                    "job_id": match.metadata.get("job_id"),
                    "score": round(match.score, 4),
                    "metadata": match.metadata,
                })

        return SearchJobsResponse(matches=matches, count=len(matches))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
