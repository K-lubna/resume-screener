from fastapi import APIRouter
from pydantic import BaseModel
from services.summarizer import summarize_text


class ChatInput(BaseModel):
    resume_text: str
    question: str

router = APIRouter()

@router.post("/ask")
def ask(body: ChatInput):
    # Simple QA: If the question asks for summary, return summary.
    q = body.question.lower()
    if "summary" in q or "overview" in q:
        return {"answer": summarize_text(body.resume_text, n_sentences=4)}
    if any(k in q for k in ["skills", "technology", "tech", "tools"]):
        skills = extract_clauses_or_sections(body.resume_text, kind="skills")
        return {"answer": ", ".join(skills)}
    # fallback: return a short extractive summary
    return {"answer": summarize_text(body.resume_text, n_sentences=3)}
