import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader

# Page setup
st.set_page_config(
    page_title="AI Resume Analyzer & Skill-Gap Finder",
    page_icon="📄",
    layout="wide"
)

st.title("📄 AI Resume Analyzer & Skill-Gap Finder")
st.markdown("Analyze your resume against any job description to evaluate ATS match scores and find skill gaps.")

# Retrieve API key automatically from Streamlit Secrets
api_key = st.secrets.get("GEMINI_API_KEY")

# Helper function to extract PDF text
def extract_pdf_text(uploaded_file):
    pdf_reader = PdfReader(uploaded_file)
    extracted_text = ""
    for page in pdf_reader.pages:
        text = page.extract_text()
        if text:
            extracted_text += text + "\n"
    return extracted_text

# Layout: Two input columns
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Upload Resume")
    uploaded_file = st.file_uploader("Upload your resume (PDF format)", type=["pdf"])

with col2:
    st.subheader("2. Target Job Description")
    job_description = st.text_area("Paste the job description or role requirements here:", height=220)

# Action button
if st.button("🚀 Analyze Resume", type="primary", use_container_width=True):
    if not api_key:
        st.error("⚠️ Gemini API Key not found. Please configure GEMINI_API_KEY in Streamlit Secrets.")
    elif uploaded_file is None:
        st.warning("⚠️ Please upload a resume in PDF format.")
    elif not job_description.strip():
        st.warning("⚠️ Please paste the target job description.")
    else:
        with st.spinner("Analyzing your resume against the job description..."):
            try:
                genai.configure(api_key=api_key)

                # Set to Gemini 3.8 Flash model
                model = genai.GenerativeModel("gemini-3.8-flash")

                resume_text = extract_pdf_text(uploaded_file)

                prompt = f"""
                You are an expert Technical Recruiter and ATS (Applicant Tracking System) specialist.
                Evaluate the candidate's resume against the provided job description.

                ---
                ### Resume Content:
                {resume_text}

                ---
                ### Job Description:
                {job_description}

                ---
                Provide an executive analysis formatted strictly with these sections:
                
                ### 1. ATS Match Score
                Provide an estimated percentage match (0-100%) and a concise one-line verdict.

                ### 2. Matching Skills & Strengths
                Bullet points of matched technologies, soft skills, and relevant experiences.

                ### 3. Missing Critical Skills & Skill Gaps
                Bullet points of required keywords, tools, or certifications missing from the resume.

                ### 4. Actionable Resume Improvement Tips
                3-4 high-impact recommendations to improve the resume for this specific role.
                """

                response = model.generate_content(prompt)

                st.success("✅ Analysis Complete!")
                st.markdown("---")
                st.markdown(response.text)

            except Exception as e:
                st.error(f"Error during analysis: {e}")
                
