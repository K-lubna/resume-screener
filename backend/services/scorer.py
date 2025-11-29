# services/scorer.py

def score_candidate(match_result):
    # match_result comes from skill_matcher.calculate_skill_score()

    resume_skills = match_result.get("resume_skills", [])
    jd_skills = match_result.get("jd_skills", [])
    matched = match_result.get("matched_skills", [])
    skill_score = match_result.get("score", 0)

    # ----------------------------------------
    # 1. Skill score = percentage returned by matcher
    # ----------------------------------------
    skills_score = int(skill_score)

    # ----------------------------------------
    # 2. Experience heuristic (optional)
    # Look for patterns like "3 years", "5+ years"
    # ----------------------------------------
    import re
    years = 0

    text = " ".join(resume_skills)  # crude but safe
    m = re.search(r"(\d+)\+?\s+years?", text)
    if m:
        years = int(m.group(1))

    experience_score = min(100, years * 12)

    # ----------------------------------------
    # 3. Final weighted score
    # ----------------------------------------
    overall = int((skills_score * 0.8) + (experience_score * 0.2))

    return {
        "skills_score": skills_score,
        "experience_score": experience_score,
        "overall_score": overall,
        "matched_skills": matched
    }
