import streamlit as st
import fitz
import os
from openai import OpenAI

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

st.title("📄 AI Resume Analyzer")
st.write(
    "Upload your resume and get AI-powered ATS analysis, "
    "skill evaluation and improvement suggestions."
)

api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))

if not api_key:
    st.error("OpenAI API key is not configured.")
    st.info(
        "Add OPENAI_API_KEY in Streamlit Secrets before using the application."
    )
    st.stop()

client = OpenAI(api_key=api_key)


def extract_text_from_pdf(uploaded_file):
    """Extract text from PDF."""

    pdf_bytes = uploaded_file.read()

    document = fitz.open(
        stream=pdf_bytes,
        filetype="pdf"
    )

    text = ""

    for page in document:
        text += page.get_text()

    document.close()

    return text


def analyze_resume(resume_text, target_role):

    prompt = f"""
You are an expert technical recruiter and ATS resume analyzer.

Analyze the following resume for the target job role:

TARGET ROLE:
{target_role}

RESUME:
{resume_text}

Provide the analysis in the following format:

# Overall ATS Score
Give a score out of 100.

# Resume Summary
Briefly explain the quality of the resume.

# Technical Skills
List the technical skills found.

# Strengths
List the strongest parts of the resume.

# Weaknesses
Identify weaknesses.

# Missing Skills
Suggest important skills that are missing for the target role.

# ATS Optimization
Suggest changes that can improve ATS compatibility.

# Project Improvements
Suggest how the projects can be made stronger.

# Action Plan
Give 5 specific improvements the candidate should make.

Do not invent experience or qualifications that are not present
in the resume.
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    return response.output_text


uploaded_file = st.file_uploader(
    "Upload your resume",
    type=["pdf"]
)

target_role = st.text_input(
    "Target Job Role",
    placeholder="Example: Python Developer"
)

if uploaded_file:

    st.success(f"Uploaded: {uploaded_file.name}")

    if st.button("🤖 Analyze Resume"):

        if not target_role.strip():
            st.warning("Please enter your target job role.")
            st.stop()

        with st.spinner("Reading resume..."):

            resume_text = extract_text_from_pdf(
                uploaded_file
            )

        if not resume_text.strip():
            st.error(
                "No readable text was found in the PDF."
            )
            st.stop()

        with st.spinner(
            "AI is analyzing your resume..."
        ):

            try:

                result = analyze_resume(
                    resume_text,
                    target_role
                )

                st.subheader(
                    "📊 AI Resume Analysis"
                )

                st.markdown(result)

                st.download_button(
                    label="⬇️ Download Analysis",
                    data=result,
                    file_name="resume_analysis.txt",
                    mime="text/plain"
                )

            except Exception as e:

                st.error(
                    f"Analysis failed: {e}"
                )


st.divider()

st.caption(
    "AI-generated analysis is intended as career guidance "
    "and should be reviewed by the candidate."
)