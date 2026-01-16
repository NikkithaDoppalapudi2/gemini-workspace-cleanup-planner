import google.generativeai as genai
import os
import streamlit as st

# Get API key from Streamlit secrets or .env
try:
    api_key = st.secrets['GEMINI_API_KEY']
except (KeyError, FileNotFoundError):
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

# Configure the client
if api_key:
    genai.configure(api_key=api_key)
else:
    st.warning("⚠️ No API key found. Please set GEMINI_API_KEY in your .env file or Streamlit secrets.")

def call_gemini(prompt):
    """Call Gemini API with the given prompt."""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        error_str = str(e)
        if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "quota" in error_str.lower():
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