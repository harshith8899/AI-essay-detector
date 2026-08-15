from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

from app.scoring import FeatureExtractionError, analyze_essay

app = FastAPI(title="AI Essay Detector")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    essay: str = Field(..., min_length=1)

    @field_validator("essay")
    @classmethod
    def essay_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("essay must not be empty or whitespace-only")
        return value


class TopFeature(BaseModel):
    name: str
    contribution: float
    plain_language_note: str


class SentenceResult(BaseModel):
    text: str
    start_offset: int
    end_offset: int
    score: float
    perplexity: float | None
    top_features: list[TopFeature]


class AnalyzeResponse(BaseModel):
    essay_score: float
    label: str
    sentences: list[SentenceResult]
    limitations: list[str]


@app.get("/")
def read_root():
    return {"status": "ok", "service": "AI Essay Detector"}


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest):
    try:
        return analyze_essay(request.essay)
    except FeatureExtractionError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
