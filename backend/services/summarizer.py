from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import re

def split_sentences(text):
    # naive split
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if len(s.strip())>20]

def summarize_text(text, n_sentences=3):
    sents = split_sentences(text)
    if not sents:
        return ""
    if len(sents) <= n_sentences:
        return " ".join(sents)
    tfidf = TfidfVectorizer(stop_words='english')
    X = tfidf.fit_transform(sents)
    scores = np.array(X.sum(axis=1)).ravel()
    top_idx = scores.argsort()[-n_sentences:][::-1]
    top_idx_sorted = sorted(top_idx)
    summary = " ".join([sents[i] for i in top_idx_sorted])
    return summary

# helper used by chat fallback
def extract_clauses_or_sections(text, kind="skills"):
    # very small heuristic for skills: look for "skills" header
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    for i, ln in enumerate(lines):
        if kind in ln.lower():
            # take next 3 lines
            return [l.strip() for l in lines[i+1:i+6] if l.strip()]
    # fallback: use skill matcher
    from services.skill_matcher import extract_skills_from_text
    return extract_skills_from_text(text)
