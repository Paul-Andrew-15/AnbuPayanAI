from dotenv import load_dotenv
import google.generativeai as genai
import streamlit as st
import os
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import io
import re
import math

# ----------------------
# Setup
# ----------------------
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash-001")

# ----------------------
# Fonts & Multilingual Setup
# ----------------------
FONT_DIR = "fonts"  # folder containing all TTF files

def register_fonts():
    pdfmetrics.registerFont(TTFont('NotoSans', os.path.join(FONT_DIR, 'NotoSans-Regular.ttf')))  # English
    pdfmetrics.registerFont(TTFont('NotoSansDevanagari', os.path.join(FONT_DIR, 'NotoSansDevanagari-Regular.ttf')))  # Hindi, Marathi
    pdfmetrics.registerFont(TTFont('NotoSansBengali', os.path.join(FONT_DIR, 'NotoSansBengali-Regular.ttf')))  # Bengali
    pdfmetrics.registerFont(TTFont('NotoSansTelugu', os.path.join(FONT_DIR, 'NotoSansTelugu-Regular.ttf')))  # Telugu
    pdfmetrics.registerFont(TTFont('NotoSansTamil', os.path.join(FONT_DIR, 'NotoSansTamil-Regular.ttf')))  # Tamil
    pdfmetrics.registerFont(TTFont('NotoSansGujarati', os.path.join(FONT_DIR, 'NotoSansGujarati-Regular.ttf')))  # Gujarati
    pdfmetrics.registerFont(TTFont('NotoSansKannada', os.path.join(FONT_DIR, 'NotoSansKannada-Regular.ttf')))  # Kannada
    pdfmetrics.registerFont(TTFont('NotoSansMalayalam', os.path.join(FONT_DIR, 'NotoSansMalayalam-Regular.ttf')))  # Malayalam

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

# ----------------------
# Budget Functions
# ----------------------
def get_budget(location, days, user_budget, people, suggestion=None, language="English"):
    base_prompt = f"""
    You are a travel budget planner. Plan a {days}-day trip for a traveler **departing from {departure}** to {location} for {people} people.

    Important rules:

    1) Validate the provided locations:
    - If the departure location or destination is missing, ambiguous, or not a real place, instruct the user clearly to provide a proper city or town name.
    - Otherwise, proceed with planning.

    2) Hotel room occupancy = 2 people per room.
    - number_of_rooms = ceil({people}/2)
    - number_of_nights = {days}
    - accommodation cost = room_rate_per_night * number_of_rooms * number_of_nights.

    3) Include travel expenses from {departure} to {location} and back in the Transport category.

    4) Output strictly plain text in {language} with NO Markdown, NO asterisks, NO backticks, NO HTML.
    Use only "|" for columns.

    5) Format:
    Category | Details (hotel/restaurant/attraction names and breakdown) | Estimated Cost (INR)

    6) Categories:
    - Transport
    - Accommodation
    - Food
    - Attractions/Activities
    - Miscellaneous

    7) End with:
    Total Estimated Cost |  | <numeric total>
    Compare the {user_budget} and Total Estimated Cost, If the user input is invalid, don't give any one liner, If {user_budget}<= Total Estimated Cost give one line as "Fits within budget" 
    OR give one line as "Exceeds budget — suggest cheaper alternatives"

    8) Important:
    - At the end, calculate the total cost and compare it with the budget accurately.
    - Perform arithmetic operations perfectly. No wrong calculations should be present.
    """


    if suggestion:
        base_prompt += f"User suggestion to apply: {suggestion}\n"

    response = model.generate_content(base_prompt)
    return response.text


def clean_response_text(text: str) -> str:
    text = re.sub(r'```[\s\S]*?```', '', text)
    text = re.sub(r'[*_`]', '', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\n\s*\n', '\n', text)
    return text.strip()


def parse_budget_text(cleaned_text: str):
    lines = cleaned_text.splitlines()
    table_data = [["Category", "Details", "Estimated Cost (INR)"]]
    notes = ""
    total_row_idx = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if re.match(r'(?i)category\s*\|\s*details.*\|\s*estimated cost', line):
            continue

        if re.search(r'Fits within budget|Exceeds budget', line, re.IGNORECASE):
            notes = line
            continue

        if re.match(r'(?i)total', line):
            parts = [p.strip() for p in line.split("|")]
            while len(parts) < 3:
                parts.append("")
            table_data.append(parts[:3])
            total_row_idx = len(table_data) - 1
            continue

        if "Total Estimated Cost" in line:
            match = re.search(r'(\d[\d,]*)', line)
            total_value = match.group(1) if match else ""
            table_data.append(["Total Estimated Cost", "", total_value])
            total_row_idx = len(table_data) - 1
            continue

        if "|" in line:
            parts = [p.strip() for p in line.split("|")]
            while len(parts) < 3:
                parts.append("")
            table_data.append(parts[:3])
            continue

        notes += (" " + line)

    return table_data, notes.strip(), total_row_idx

def generate_pdf(table_data, notes, language="English", highlight_row_idx=None, filename="budget.pdf"):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=18, leftMargin=18, topMargin=18, bottomMargin=18)
    styles = getSampleStyleSheet()
    elements = []

    font_name = LANG_FONT_MAP.get(language, "NotoSans")
    normal_style = ParagraphStyle(name='Normal', fontName=font_name, fontSize=9)
    title_style = ParagraphStyle(name='Title', fontName=font_name, fontSize=18, leading=22)
    
    elements.append(Paragraph("Travel Budget Recommendation", title_style))
    elements.append(Spacer(1, 12))

    wrapped_data = []
    for row in table_data:
        wrapped_row = [Paragraph(str(cell), normal_style) for cell in row]
        wrapped_data.append(wrapped_row)

    col_widths = [120, 260, 100]
    table = Table(wrapped_data, colWidths=col_widths)
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4B9CD3")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
    ])
    if highlight_row_idx is not None and 0 <= highlight_row_idx < len(wrapped_data):
        style.add('BACKGROUND', (0, highlight_row_idx), (-1, highlight_row_idx), colors.HexColor("#FFF2CC"))

    table.setStyle(style)
    elements.append(table)

    elements.append(Spacer(1, 12))
    if notes:
        elements.append(Paragraph(f"<b>Notes:</b> {notes}", normal_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer

# ----------------------
# Streamlit UI
# ----------------------
st.set_page_config(page_title="AnbuPayanAI")
st.header("Budget Recommendation System")

departure = st.text_input("Enter your departure location:", key="departure")
location = st.text_input("Enter destination you are visiting:", key="location")
days = st.number_input("Enter number of days:", min_value=1, step=1, key="days")
people = st.number_input("Enter number of people:", min_value=1, step=1, key="people")
user_budget = st.number_input("Enter your budget (INR):", min_value=1000, step=500, key="budget")
language = st.selectbox("Select Language", list(LANG_FONT_MAP.keys()))

# Session state
if "base_budget" not in st.session_state:
    st.session_state.base_budget = None
if "custom_budget" not in st.session_state:
    st.session_state.custom_budget = None

# --- Base Budget ---
if st.button("Get Budget Plan"):
    if not departure or not location or not days or not user_budget or not people:
        st.warning("Please provide all primary details: departure location, destination, number of days, number of people, and budget.")
    else:
        raw = get_budget(
        location=f"{departure} to {location}",
        days=days,
        user_budget=user_budget,
        people=people,
        language=language
        )
        cleaned = clean_response_text(raw)
        st.session_state.base_budget = cleaned
       

if st.session_state.base_budget:
    table_data, notes, total_row_idx = parse_budget_text(st.session_state.base_budget)

    st.subheader("Estimated Budget Plan")
    st.table(table_data)
    if notes:
        st.write(f"**Notes:** {notes}")

    pdf_buffer = generate_pdf(table_data, notes, language=language, highlight_row_idx=total_row_idx)
    st.download_button("Download Budget as PDF", data=pdf_buffer, file_name="travel_budget.pdf", mime="application/pdf")

    # Suggestions
    st.subheader("Want to customize the budget further?")
    user_suggestion = st.text_area("Enter your suggestions:", key="suggestion")

    if st.button("Generate New Budget with Suggestions"):
        if user_suggestion.strip():
            raw = get_budget(
                location=f"{departure} to {location}",
                days=days,
                user_budget=user_budget,
                people=people,
                suggestion=user_suggestion,
                language=language
            )
            cleaned = clean_response_text(raw)
            st.session_state.custom_budget = cleaned
        else:
            st.warning("Please enter a suggestion before generating a new budget.")

# --- Customized Budget ---
if st.session_state.custom_budget:
    table_data_s,notes_s, total_row_idx_s = parse_budget_text(st.session_state.custom_budget)

    st.subheader("Customized Budget Plan (with your suggestion)")
    st.table(table_data_s)
    if notes_s:
        st.write(f"**Notes:** {notes_s}")

    pdf_buffer_s = generate_pdf(table_data_s, notes_s, language=language, highlight_row_idx=total_row_idx_s)
    st.download_button("Download Customized Budget as PDF", data=pdf_buffer_s, file_name="travel_budget_customized.pdf", mime="application/pdf")
