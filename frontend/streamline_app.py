import streamlit as st
import requests
import pandas as pd

API_BASE = "http://127.0.0.1:8000"

st.set_page_config(page_title="Resume Screener", layout="wide")
st.sidebar.title("Resume Screener")
mode = st.sidebar.radio("Mode", ["Single Resume", "Batch Compare", "Upload JD"])

if mode == "Upload JD":
    st.header("Upload / Paste Job Description")
    jd_text = st.text_area("Paste JD here", height=300)
    if st.button("Parse JD", key="parse_jd"):
        res = requests.post(f"{API_BASE}/analyze/parse_jd", json={"jd_text": jd_text})
        st.json(res.json())

elif mode == "Single Resume":
    st.header("Analyze Single Resume vs JD")
    jd_text = st.text_area("Paste JD (optional)", height=150)
    uploaded = st.file_uploader("Upload Resume (PDF / DOCX)", type=["pdf","docx"])
    if uploaded:
        files = {"file": (uploaded.name, uploaded.getvalue())}
        res = requests.post(f"{API_BASE}/upload/resume", files=files)
        parsed = res.json()
        st.subheader("Parsed Resume")
        st.write("Name guess:", parsed.get("name"))
        st.text_area("Extracted Text", parsed.get("text")[:2000], height=250)
        if st.button("Analyze", key="analyze_single"):
            resume_text = parsed.get("text")
            jd_skills = []
            if jd_text.strip():
                jd_parsed = requests.post(f"{API_BASE}/analyze/parse_jd", json={"jd_text": jd_text}).json()
                jd_skills = jd_parsed.get("skills", [])
            payload = {"resume_text": resume_text, "resume_meta": {"jd_skills": jd_skills}}
            res2 = requests.post(f"{API_BASE}/analyze/analyze_resume", json=payload).json()
            st.metric("Overall Score", res2["scores"]["overall"])
            st.subheader("Summary")
            st.write(res2["summary"])
            st.subheader("Matched Skills")
            st.json(res2["matches"])

elif mode == "Batch Compare":
    st.header("Batch Compare Resumes")
    jd_text = st.text_area("Paste JD (optional)", height=150)
    uploaded = st.file_uploader("Upload multiple resumes (PDF / DOCX)", type=["pdf","docx"], accept_multiple_files=True)
    if st.button("Run Compare", key="batch_compare_btn") and uploaded:
        resumes = []
        for f in uploaded:
            res = requests.post(f"{API_BASE}/upload/resume", files={"file": (f.name, f.getvalue())})
            parsed = res.json()
            resumes.append({"name": parsed.get("name"), "resume_text": parsed.get("text")})

        jd_skills = []
        if jd_text.strip():
            jd_parsed = requests.post(f"{API_BASE}/analyze/parse_jd", json={"jd_text": jd_text}).json()
            jd_skills = jd_parsed.get("skills", [])

        payload = {"resumes": resumes, "jd_skills": jd_skills}
        try:
            res3 = requests.post(f"{API_BASE}/compare/compare", json=payload).json()
            df = pd.DataFrame([{"name": r["name"], "overall": r["scores"]["overall"]} for r in res3["ranked"]])
            st.dataframe(df.sort_values("overall", ascending=False))
            st.subheader("All Results")
            st.json(res3)
        except Exception as e:
            st.error(f"Error during batch compare: {e}")
