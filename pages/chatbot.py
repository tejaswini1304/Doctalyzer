import streamlit as st
import google.generativeai as genai
import time
from dotenv import load_dotenv
from deep_translator import GoogleTranslator
import os

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

# Translate response
def translate_text(text, lang_code):
    try:
        return GoogleTranslator(source='auto', target=lang_code).translate(text)
    except Exception as e:
        st.warning(f"Translation failed: {e}")
        return text

# Gemini chatbot logic
def ask_agent(question, language="en"):
    prompt = f"Answer this query politely and clearly like a customer support agent: {question}"
    for attempt in range(MAX_RETRIES):
        try:
            response = model.generate_content(prompt)
            answer = response.text
            return translate_text(answer, language)
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
            else:
                return "Sorry, I'm unable to answer that right now."

# SmatBot-style Chat UI
def chat_ui():
    st.title("💬 SmatBot Chat Assistant")
    st.caption("Ask anything! Your virtual assistant is ready to chat.")

    USER_AVATAR = "🧑‍💻"
    AGENT_AVATAR = "🤖"

    language = st.selectbox("Choose Language", list(lang_codes.keys()))
    lang_code = lang_codes[language]

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if not any("joined" in msg for msg in st.session_state.chat_history):
        st.session_state.chat_history.append({"sender": "agent", "message": "Agent Surya joined the chat ✅", "joined": True})

    # Show chat history
    for chat in st.session_state.chat_history:
        if "joined" in chat:
            st.markdown(f"###### 👋 {chat['message']}")
        elif chat["sender"] == "user":
            with st.chat_message(USER_AVATAR):
                st.markdown(chat["message"])
        else:
            with st.chat_message(AGENT_AVATAR):
                st.markdown(chat["message"])

    # Input message
    user_input = st.chat_input("Type your message...")
    if user_input:
        st.session_state.chat_history.append({"sender": "user", "message": user_input})
        with st.chat_message(USER_AVATAR):
            st.markdown(user_input)

        with st.chat_message(AGENT_AVATAR):
            with st.spinner("Agent is typing..."):
                reply = ask_agent(user_input, lang_code)
                st.session_state.chat_history.append({"sender": "agent", "message": reply})
                st.markdown(reply)

# Run the chatbot
if __name__ == "_main_":
    chat_ui()