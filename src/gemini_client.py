from google import genai
import os
import streamlit as st
import time

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
        error_str = str(e)
        if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
            st.error("🚫 Gemini API Quota Exceeded")
            st.warning("""
            **Free Tier Limit Reached**
            
            You've exceeded Google's free Gemini API quota. Here's what you can do:
            
            1. **Wait**: Free quota resets daily (usually around midnight UTC)
            2. **Upgrade**: Enable billing in Google Cloud Console for higher limits
            3. **Monitor Usage**: Check [Google AI Studio](https://aistudio.google.com/) for current usage
            
            **Alternative**: Try again in a few hours when quota resets.
            """)
            return "Error: API quota exceeded. Please try again later or upgrade your plan."
        else:
            st.error(f"Gemini API error: {error_str}")
            return f"Error: {error_str}"