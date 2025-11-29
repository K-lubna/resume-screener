from fastapi import APIRouter
from pydantic import BaseModel
from services.scorer import score_candidate
from services.skill_matcher import extract_skills_from_text

class CompareInput(BaseModel):
    resumes: list  # list of {"resume_text": str, "name": str}
    jd_skills: list = []

router = APIRouter()

@router.post("/compare")
def compare(body: CompareInput):
    results = []
    for r in body.resumes:
        skills = extract_skills_from_text(r["resume_text"])
        match = {"name": r.get("name",""), "skills": skills}
        scores = score_candidate({"matched": list(set(skills).intersection(set(body.jd_skills))),
                                  "required": body.jd_skills,
                                  "found": skills})
        results.append({"name": r.get("name",""), "skills": skills, "scores": scores})
    # ranking by overall_score desc
    ranked = sorted(results, key=lambda x: x["scores"]["overall"], reverse=True)
    return {"ranked": ranked}
