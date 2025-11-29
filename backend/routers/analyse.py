from fastapi import APIRouter
from pydantic import BaseModel
from services.jd_parser import parse_jd_text
from services.skill_matcher import match_skills
from services.scorer import score_candidate
from services.summarizer import summarize_text

class JDInput(BaseModel):
    jd_text: str

class ResumeInput(BaseModel):
    resume_text: str
    resume_meta: dict = {}

router = APIRouter()

@router.post("/parse_jd")
def parse_jd(body: JDInput):
    jd = parse_jd_text(body.jd_text)
    return jd

@router.post("/analyze_resume")
def analyze_resume(body: ResumeInput):
    jd_skills = body.resume_meta.get("jd_skills", [])  # optional
    # skill matching
    matches = match_skills(body.resume_text, jd_skills)
    summary = summarize_text(body.resume_text, n_sentences=3)
    scores = score_candidate(matches)
    return {
        "summary": summary,
        "matches": matches,
        "scores": scores
    }
