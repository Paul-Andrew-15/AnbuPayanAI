import os
import io
import re
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash-exp")

FONT_DIR = "fonts"

def register_fonts():
    pdfmetrics.registerFont(TTFont('NotoSans', os.path.join(FONT_DIR, 'NotoSans-Regular.ttf')))
    pdfmetrics.registerFont(TTFont('NotoSansDevanagari', os.path.join(FONT_DIR, 'NotoSansDevanagari-Regular.ttf')))
    pdfmetrics.registerFont(TTFont('NotoSansBengali', os.path.join(FONT_DIR, 'NotoSansBengali-Regular.ttf')))
    pdfmetrics.registerFont(TTFont('NotoSansTelugu', os.path.join(FONT_DIR, 'NotoSansTelugu-Regular.ttf')))
    pdfmetrics.registerFont(TTFont('NotoSansTamil', os.path.join(FONT_DIR, 'NotoSansTamil-Regular.ttf')))
    pdfmetrics.registerFont(TTFont('NotoSansGujarati', os.path.join(FONT_DIR, 'NotoSansGujarati-Regular.ttf')))
    pdfmetrics.registerFont(TTFont('NotoSansKannada', os.path.join(FONT_DIR, 'NotoSansKannada-Regular.ttf')))
    pdfmetrics.registerFont(TTFont('NotoSansMalayalam', os.path.join(FONT_DIR, 'NotoSansMalayalam-Regular.ttf')))

LANG_FONT_MAP = {
    "English": "NotoSans",
    "Hindi": "NotoSansDevanagari",
    "Bengali": "NotoSansBengali",
    "Telugu": "NotoSansTelugu",
    "Marathi": "NotoSansDevanagari",
    "Tamil": "NotoSansTamil",
    "Gujarati": "NotoSansGujarati",
    "Kannada": "NotoSansKannada",
    "Malayalam": "NotoSansMalayalam",
}

register_fonts()

def generate_pdf(itinerary_text, language="English", filename="itinerary.pdf"):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=18, leftMargin=18, topMargin=18, bottomMargin=18)
    styles = getSampleStyleSheet()
    
    font_name = LANG_FONT_MAP.get(language, "NotoSans")
    normal_style = ParagraphStyle(name='Normal', fontName=font_name, fontSize=10, leading=14)
    title_style = ParagraphStyle(name='Title', fontName=font_name, fontSize=16, leading=20)
    
    elements = []
    elements.append(Paragraph("Personalized Travel Itinerary", title_style))
    elements.append(Spacer(1, 12))
    
    # Split itinerary by lines and add paragraphs
    for line in itinerary_text.splitlines():
        if line.strip():
            elements.append(Paragraph(line, normal_style))
            elements.append(Spacer(1, 4))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

def clean_response_text(text: str) -> str:
    text = re.sub(r'```[\s\S]*?```', '', text)
    text = re.sub(r'[*_`]', '', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\n\s*\n', '\n', text)
    return text.strip()

def generate_itinerary(departure, destination, days, budget, interests, language, suggestion=None):
    prompt = f"""
    You are an expert travel planner AI.

    Task:
    Create a detailed {days}-day itinerary for a traveler departing from {departure} to {destination}.

    Traveler details:
    - Departure: {departure}
    - Destination: {destination}
    - Budget: ₹{budget}
    - Interests: {interests}
    - Language: {language}

    Validation Rules:
    1) If departure or destination is missing, ambiguous, or not a real place, STOP and ask the user to provide a proper city or town name.
    2) If number of days, budget, or people count is invalid (e.g., zero, negative, or unrealistic), STOP and ask the user to correct the details.
    3) If inputs are valid, proceed with generating the itinerary.

    Output Rules:
    1) The entire response MUST be written in {language}.
    2) Don't say Here's the output, I will generate the content kind of sentence. Just start from Day 1 Itinerary generation. It should be followed for every languages.
    2) The itinerary must be structured day-wise:
    - Start each day with "Day X:" on a new line.
    - Use separate lines for Morning, Afternoon, and Evening plans.
    - Keep descriptions short, clear, and easy to read.
    3) Use "|" ONLY when separating Category/Activity/Cost in the final cost summary.
    4) Output must be plain text only — NO Markdown, NO HTML, NO code blocks.
    5) Include costs for travel, accommodation, food, and activities each day.
    6) At the end, give a clean cost summary table-like format:
    Category | Estimated Cost (INR)
    ...
    Total Estimated Cost | <amount>
    7) Finally, state whether it "Fits within budget" or "Exceeds budget".
    """


    if suggestion:
        prompt += f"\nUser suggestion to adjust itinerary: {suggestion}\n"
    
    response = model.generate_content(prompt)
    return clean_response_text(response.text)

st.set_page_config(page_title="Itinerary Generator", layout="wide")
st.title("✈️ Personalized Itinerary Generator")

departure = st.text_input("Enter Departure Location:", "Chennai")
destination = st.text_input("Enter Destination:", "Bangalore")
days = st.number_input("Trip Duration (days):", min_value=1, max_value=30, value=3)
budget = st.number_input("Budget (INR):", min_value=1000, max_value=1000000, value=20000)
interests = st.text_area("Enter your interests (comma-separated):", "Food, Adventure, Culture")
language = st.selectbox("Output Language:", list(LANG_FONT_MAP.keys()))

if "itinerary" not in st.session_state:
    st.session_state.itinerary = None
if "custom_itinerary" not in st.session_state:
    st.session_state.custom_itinerary = None

if st.button("Generate Itinerary"):
    if not departure or not destination or not days or not budget or not interests or not language:
        st.warning("Please provide all primary details: departure location, destination, number of days, number of people, budget, interests, and language.")
    else:
        with st.spinner("Generating itinerary..."):
            st.session_state.itinerary = generate_itinerary(departure, destination, days, budget, interests, language)
            st.session_state.custom_itinerary = None

if st.session_state.itinerary:
    st.subheader("Generated Itinerary")
    st.text(st.session_state.itinerary)
    pdf_buffer = generate_pdf(st.session_state.itinerary, language=language)
    st.download_button("Download Itinerary as PDF", data=pdf_buffer, file_name="itinerary.pdf", mime="application/pdf")

    st.subheader("Customize Your Itinerary")
    user_suggestion = st.text_area("Enter your suggestions/preferences to adjust the itinerary:", key="suggestion_input")
    if st.button("Regenerate Itinerary with Suggestions"):
        if user_suggestion.strip():
            with st.spinner("Regenerating itinerary based on your suggestion..."):
                st.session_state.custom_itinerary = generate_itinerary(departure, destination, days, budget, interests, language, suggestion=user_suggestion)
        else:
            st.warning("Please enter a suggestion to regenerate itinerary.")

if st.session_state.custom_itinerary:
    st.subheader("Customized Itinerary (with your suggestion)")
    st.text(st.session_state.custom_itinerary)
    pdf_buffer_custom = generate_pdf(st.session_state.custom_itinerary, language=language)
    st.download_button("Download Customized Itinerary as PDF", data=pdf_buffer_custom, file_name="custom_itinerary.pdf", mime="application/pdf")

