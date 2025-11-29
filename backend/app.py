# app.py
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from typing import List, Dict
import tempfile
import pdfplumber
from docx import Document

app = FastAPI()

# Models
class JDPayload(BaseModel):
    jd_text: str

class ResumePayload(BaseModel):
    resume_text: str
    resume_meta: Dict = {}

class BatchComparePayload(BaseModel):
    resumes: List[Dict]
    jd_skills: List[str] = []

# Utilities
def parse_resume_file(file: UploadFile) -> Dict:
    with tempfile.NamedTemporaryFile(delete=False, suffix=file.filename) as tmp:
        tmp.write(file.file.read())
        tmp_path = tmp.name

    text = ""
    if file.filename.endswith(".pdf"):
        try:
            with pdfplumber.open(tmp_path) as pdf:
                text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
        except Exception as e:
            text = ""
    elif file.filename.endswith(".docx"):
        try:
            doc = Document(tmp_path)
            text = "\n".join(para.text for para in doc.paragraphs)
        except Exception as e:
            text = ""
    else:
        text = file.file.read().decode("utf-8", errors="ignore")

    return {"name": file.filename.split(".")[0], "text": text}


def extract_skills_from_jd(jd_text: str) -> List[str]:
    import re
    tech_keywords = ["Python", "Java", "C++", "SQL", "Machine Learning", "AWS", "React"]
    found = []

    # Look for keywords
    for kw in tech_keywords:
        if kw.lower() in jd_text.lower():
            found.append(kw)

    # Capitalized words
    words = re.findall(r'\b[A-Z][a-zA-Z]+\b', jd_text)
    found.extend([w for w in words if w not in found])

    return list(set(found))


def analyze_resume_text(resume_text: str, jd_skills: List[str]) -> Dict:
    if not resume_text:
        return {"scores": {"overall": 0}, "summary": "No text found", "matches": []}

    resume_lower = resume_text.lower()
    matched = [s for s in jd_skills if s.lower() in resume_lower]
    overall = len(matched) / len(jd_skills) if jd_skills else 0.0

    return {
        "scores": {"overall": round(overall, 2)},
        "summary": f"{len(matched)} out of {len(jd_skills)} skills matched",
        "matches": matched
    }

# Endpoints
@app.post("/analyze/parse_jd")
def parse_jd(jd: JDPayload):
    skills = extract_skills_from_jd(jd.jd_text)
    return {"skills": skills}


@app.post("/upload/resume")
async def upload_resume(file: UploadFile = File(...)):
    parsed = parse_resume_file(file)
    return parsed


@app.post("/analyze/analyze_resume")
def analyze_resume(payload: ResumePayload):
    resume_text = payload.resume_text
    jd_skills = payload.resume_meta.get("jd_skills", [])
    result = analyze_resume_text(resume_text, jd_skills)
    return result


@app.post("/compare/compare")
def compare_resumes(payload: BatchComparePayload):
    results = []

    for r in payload.resumes:
        name = r.get("name", "Unknown")
        text = r.get("resume_text", "")

        # Ensure non-empty text
        if not text or text.strip() == "":
            results.append({"name": name, "scores": {"overall": 0}})
            continue

        try:
            scores = analyze_resume_text(text, payload.jd_skills)
            # Make sure 'overall' exists
            if "scores" not in scores or "overall" not in scores["scores"]:
                scores = {"scores": {"overall": 0}, "summary": "", "matches": []}
        except Exception as e:
            print(f"Error analyzing resume '{name}': {e}")
            scores = {"scores": {"overall": 0}, "summary": "", "matches": []}

        results.append({"name": name, "scores": scores["scores"], "summary": scores.get("summary",""), "matches": scores.get("matches",[])})

    ranked = sorted(results, key=lambda x: x["scores"]["overall"], reverse=True)
    return {"ranked": ranked}
