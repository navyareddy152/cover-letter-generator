import streamlit as st
import PyPDF2
import io
import google.generativeai as genai

# ---------------------------
# Config
# ---------------------------
# Gemini API key setup 
API_KEY = "AIzaSyAN6q-Ppcw2-pAqfn0wadrWRvH23NaTHws"
genai.configure(api_key=API_KEY)

# ---------------------------
# Helper: Extract text from PDF
# ---------------------------
def extract_pdf_text(uploaded_file):
    """
    Reads and extracts all text from a PDF file uploaded by the user.
    """
    try:
        reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Couldn't read your PDF. Error: {e}")
        return None

# ---------------------------
# Helper: Generate Cover Letter using Gemini
# ---------------------------
def generate_cover_letter(resume_text, job_desc):
    """
    Uses Gemini 2.0 Flash model to generate a tailored cover letter.
    """
    prompt = f"""
    You are a professional career coach. Write a compelling and personalized cover letter based on:

    Job Description:
    {job_desc}

    Resume:
    {resume_text}

    Please use a professional tone, structure the letter formally, and highlight key skills that align with the job.
    """

    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.7,
                "max_output_tokens": 700
            }
        )

        # Get the response content safely
        if response.candidates and \
           response.candidates[0].content and \
           response.candidates[0].content.parts:
            return response.candidates[0].content.parts[0].text
        else:
            st.error("Hmm... the AI didn’t return any text. Try again.")
            return None
    except Exception as e:
        st.error(f"Something went wrong while generating your letter: {e}")
        return None

# ---------------------------
# Streamlit UI
# ---------------------------
st.set_page_config(page_title="AI Cover Letter Generator", layout="centered")

st.title("📄 AI-Powered Cover Letter Generator")
st.markdown("Upload your **resume (PDF)** and paste a **job description**. I’ll help you write a professional cover letter in seconds.")

# Upload resume
uploaded_resume = st.file_uploader("Upload Resume (PDF only)", type=["pdf"])

# Job description input
job_description = st.text_area("Paste the Job Description", height=300, placeholder="e.g., We're looking for a Data Analyst skilled in Python, SQL, and Tableau...")

# Trigger generation
if st.button("✨ Generate Cover Letter"):
    if uploaded_resume is not None and job_description.strip():
        with st.spinner("Reading your resume..."):
            resume_text = extract_pdf_text(uploaded_resume)

        if resume_text:
            with st.spinner("Writing your cover letter..."):
                cover_letter = generate_cover_letter(resume_text, job_description)

            if cover_letter:
                st.success("✅ Done! Here’s your cover letter:")
                st.subheader("🎯 Generated Cover Letter")
                st.markdown(f"```text\n{cover_letter}\n```")

                st.download_button(
                    label="⬇️ Download as .txt",
                    data=cover_letter,
                    file_name="cover_letter.txt",
                    mime="text/plain"
                )
            else:
                st.error("Failed to generate the letter. Please try again.")
        else:
            st.error("Couldn't read your resume. Please upload a valid PDF.")
    else:
        st.warning("Please upload a resume and paste a job description.")
