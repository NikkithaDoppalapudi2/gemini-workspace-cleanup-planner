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

try:
    client = genai.Client(api_key=api_key)
except Exception as e:
    st.error(f"Failed to initialize Gemini client: {str(e)}")
    st.stop()

def call_gemini(prompt):
    try:
        response = client.models.generate_content(model='gemini-2.0-flash-exp', contents=prompt)
        return response.text
    except Exception as e:
        st.error(f"Gemini API error: {str(e)}")
        return "Error: Unable to generate response. Please check your API key and try again."