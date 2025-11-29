import re
from sentence_transformers import SentenceTransformer, util

_model = None

def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer('all-mpnet-base-v2')
    return _model

def extract_skills_from_text(text):
    # naive: split on commas and lines; plus regex for technologies
    tech_pattern = r"\b(Python|Java|C\+\+|C#|JavaScript|TypeScript|React|Node\.js|Node|Django|Flask|SQL|Postgres|MySQL|MongoDB|AWS|Azure|GCP|Docker|Kubernetes|TensorFlow|PyTorch|scikit-learn|NLP|Machine Learning|ML)\b"
    found = re.findall(tech_pattern, text, re.IGNORECASE)
    skills = list(dict.fromkeys([f.lower() for f in found]))
    # also find typical skill-lines
    lines = [l.strip() for l in re.split(r'\n|;|-', text) if 3 < len(l) < 120]
    # add tokens that look like skills (comma separated)
    for ln in lines[:40]:
        if ',' in ln:
            parts = [p.strip().lower() for p in ln.split(',') if len(p.strip())>1]
            for p in parts:
                if len(p) < 40 and len(p) > 1:
                    skills.append(p)
    # dedupe
    skills = list(dict.fromkeys(skills))
    return skills

def match_skills(resume_text, jd_skills):
    # compute matches and semantic similarity using embeddings
    model = _get_model()
    resume_skills = extract_skills_from_text(resume_text)
    matched = []
    sim_scores = {}
    if jd_skills:
        emb_jd = model.encode([s for s in jd_skills], convert_to_tensor=True)
        emb_resume = model.encode([s for s in resume_skills], convert_to_tensor=True)
        cos = util.cos_sim(emb_jd, emb_resume).cpu().numpy()
        for i, jd in enumerate(jd_skills):
            # find best matching resume skill
            best_idx = cos[i].argmax()
            best_score = float(cos[i][best_idx])
            if best_score > 0.55:
                matched.append(resume_skills[best_idx])
                sim_scores[jd] = {"matched": resume_skills[best_idx], "score": round(best_score,3)}
            else:
                sim_scores[jd] = {"matched": None, "score": round(best_score,3)}
    return {"found_skills": resume_skills, "matched_to_jd": matched, "sim_scores": sim_scores}
