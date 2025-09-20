import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel("gemini-2.0-flash-001")

st.set_page_config(page_title="AnbuPayanAI")
st.title("🌍AnbuPayanAI")
st.header("Multilingual Chatbot")

language = st.selectbox(
    "Select language",
    ['English','Hindi','Bengali','Telugu','Marathi','Tamil','Gujarati','Kannada','Malayalam']
)

if 'chat_session' not in st.session_state:
    st.session_state['chat_session'] = model.start_chat(history=[])

if 'chat_display' not in st.session_state:
    st.session_state['chat_display'] = [] 

def gemini_response(language, user_input, chat_session):
    prompt = f"""
You are a friendly multilingual chatbot that helps users with trip planning and bookings.

Rules:
1. Always respond in {language}.
2. Give short and precise answers in bullet points.
3. Remember user details like budget, destination, travel dates, and preferences during the conversation.
4. Only answer trip planning or user info questions. If the question is unrelated, reply: "Please ask relevant questions."
5. Trip planning includes:
   - Budget suggestions
   - Destinations
   - Flight booking
   - Train booking
   - Bus booking
   - Hotels
   - Places to visit
   - Other travel services available on platforms like EaseMyTrip
6. If you are not sure about something, say "I don’t know" instead of making things up.
7. Give step-by-step guidance for bookings (like how to search for flights/trains/buses, best timing, tips, etc.).
8. After every response, ask one relevant follow-up question to guide the user in planning their trip.
"""

    response = chat_session.send_message(f"{prompt}\nUser: {user_input}")
    return response.text

user_input = st.chat_input("Ask the question", key="input")

if user_input:
    response = gemini_response(language, user_input, st.session_state['chat_session'])
    st.session_state['chat_display'].append(("You", user_input))
    st.session_state['chat_display'].append(("Bot", response))

for sender, msg in st.session_state['chat_display']:
    if sender == "You":
        st.chat_message("user").write(msg)
    else:
        st.chat_message("assistant").write(msg)


