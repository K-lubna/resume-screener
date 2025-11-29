import re

def parse_jd_text(jd_text: str):
    # basic heuristics: look for "requirements", "skills", "responsibilities"
    sections = {}
    jj = jd_text.lower()
    # find skills line patterns
    skills = []
    for m in re.finditer(r"(skills|requirements|must have|should have)[:\-]?(.*)", jd_text, flags=re.IGNORECASE):
        rest = m.group(2)
        # split commas
        parts = [p.strip() for p in re.split(r",|\n|;| or ", rest) if p.strip()]
        skills.extend(parts)
    # fallback: scan for known tech keywords (common list)
    if not skills:
        known = ["python","java","c++","react","node","sql","aws","docker","kubernetes","ml","nlp"]
        for k in known:
            if k in jj:
                skills.append(k)
    return {"skills": list(dict.fromkeys([s.lower() for s in skills]))}
