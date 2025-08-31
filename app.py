# app.py

import streamlit as st

# Configure Streamlit page
st.set_page_config(page_title="NLP Healthcare App", layout="wide")

# Sidebar for navigation
st.sidebar.title("Navigation")
selected_page = st.sidebar.radio("Go to", ["🩺 Medical Report Analyzer", "💬 SmatBot Chat Assistant"])

# Route to corresponding page
if selected_page == "🩺 Medical Report Analyzer":
    from pages import doctalyzer
    doctalyzer.main()

elif selected_page == "💬 SmatBot Chat Assistant":
    from pages import chatbot
    chatbot.chat_ui()
