import streamlit as st
import google.generativeai as genai
from PIL import Image
import PyPDF2
import tempfile
import os
from google.api_core import exceptions
from dotenv import load_dotenv
from deep_translator import GoogleTranslator
import time

# Load environment variables
load_dotenv()

# Gemini API key
api_key = "AIzaSyARijCtBznAFTO2g0zWkOCI2SyFuVCvEfw"
if not api_key:
    st.error("Gemini API key not found.")
    st.stop()

# Configure Gemini
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

# Language options
lang_codes = {
    "English": "en",
    "Hindi": "hi",
    "Marathi": "mr"
}

# Function to translate text
def translate_text(text, lang_code):
    try:
        return GoogleTranslator(source='auto', target=lang_code).translate(text)
    except Exception as e:
        st.warning(f"Translation failed: {e}")
        return text

# Analyze medical report
def analyze_medical_report(content, content_type, layman=False):
    if layman:
        prompt = "Explain this medical report in very simple, layman-friendly terms so that a patient with no medical background can understand it clearly."
    else:
        prompt = "Analyze this medical report concisely. Provide key findings, diagnoses, and recommendations."

    for attempt in range(MAX_RETRIES):
        try:
            if content_type == "image":
                response = model.generate_content([prompt, content])
            else:
                response = model.generate_content(f"{prompt}\n\n{content}")
            return response.text
        except exceptions.GoogleAPIError as e:
            if attempt < MAX_RETRIES - 1:
                st.warning(f"Error occurred. Retrying in {RETRY_DELAY}s... (Attempt {attempt + 1})")
                time.sleep(RETRY_DELAY)
            else:
                st.error("Gemini failed to analyze the report.")
                return fallback_analysis(content, content_type)

# Fallback analysis when AI fails
def fallback_analysis(content, content_type):
    st.warning("Using fallback analysis due to Gemini issues.")
    if content_type == "image":
        return "Image analysis is currently unavailable. Try again later or consult a professional."
    else:
        word_count = len(content.split())
        return f"""
        Fallback Summary:
        - Document Type: Text
        - Word Count: ~{word_count} words
        - Note: AI analysis is temporarily unavailable.
        - Recommendation: Please consult a healthcare provider.
        """

# Extract text from PDF
def extract_text_from_pdf(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def main():
    st.title("🩺Doctalyzer")
    st.write("Upload a medical report (Image or PDF). Choose language. Get AI-based analysis + simplified explanation.")

    file_type = st.radio("Select file type:", ("Image", "PDF"))
    language = st.selectbox("Choose Output Language", list(lang_codes.keys()))

    if file_type == "Image":
        uploaded_file = st.file_uploader("Upload medical report image", type=["jpg", "jpeg", "png"])
        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_column_width=True)

            if st.button("Analyze Image"):
                with st.spinner("Analyzing report..."):
                    analysis = analyze_medical_report(image, "image")
                    layman_summary = analyze_medical_report(image, "image", layman=True)

                    translated_analysis = translate_text(analysis, lang_codes[language])
                    translated_summary = translate_text(layman_summary, lang_codes[language])

                    st.subheader("🔬 AI Medical Analysis")
                    st.write(translated_analysis)

                    st.subheader("🧑‍⚕ Patient-Friendly Summary")
                    st.write(translated_summary)

    elif file_type == "PDF":
        uploaded_file = st.file_uploader("Upload medical report PDF", type=["pdf"])
        if uploaded_file:
            if st.button("Analyze PDF"):
                with st.spinner("Extracting and analyzing PDF..."):
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_path = tmp_file.name

                    with open(tmp_path, "rb") as f:
                        pdf_text = extract_text_from_pdf(f)

                    os.unlink(tmp_path)

                    analysis = analyze_medical_report(pdf_text, "text")
                    layman_summary = analyze_medical_report(pdf_text, "text", layman=True)

                    translated_analysis = translate_text(analysis, lang_codes[language])
                    translated_summary = translate_text(layman_summary, lang_codes[language])

                    st.subheader("🔬 AI Medical Analysis")
                    st.write(translated_analysis)

                    st.subheader("🧑‍⚕ Patient-Friendly Summary")
                    st.write(translated_summary)

if __name__ == "_main_":
    main()