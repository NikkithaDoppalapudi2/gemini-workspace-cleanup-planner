from google import genai
import os
import streamlit as st

# Get API key from Streamlit secrets or .env
try:
    api_key = st.secrets['GEMINI_API_KEY']
except (KeyError, FileNotFoundError):
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

def call_gemini(prompt):
    response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
    return response.text