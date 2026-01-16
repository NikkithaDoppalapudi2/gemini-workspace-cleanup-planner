import google.generativeai as genai
import os
import streamlit as st
import time
import random

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

def call_gemini(prompt, max_retries=3):
    """Call Gemini API with the given prompt and exponential backoff retry logic."""
    if not api_key:
        return "Error: No API key configured."

    model = genai.GenerativeModel('gemini-1.5-flash')
    
    for attempt in range(max_retries):
        try:
            # Add a small random jitter before each retry (except the first)
            if attempt > 0:
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                time.sleep(wait_time)
            
            response = model.generate_content(prompt)
            # Check if response has text (it might be blocked by safety)
            if response.candidates:
                candidate = response.candidates[0]
                if candidate.content.parts:
                    return candidate.content.parts[0].text
                else:
                    return "Error: Empty response. Possible safety filter block."
            else:
                return "Error: No candidates returned. Possible safety filter block."
            
        except Exception as e:
            error_str = str(e)
            
            # Check for Resource Exhausted (429) or other quota errors
            if any(indicator in error_str.lower() for indicator in ["429", "resource_exhausted", "quota", "too many requests"]):
                if attempt < max_retries - 1:
                    # Log retry attempt in Streamlit if possible
                    st.toast(f"⏳ API Limit hit. Retrying in {2**(attempt+1)}s... (Attempt {attempt+1}/{max_retries})")
                    continue 
                else:
                    st.error("🚫 Gemini API Quota Exceeded after multiple retries.")
                    st.warning("""
                    **Free Tier Limit Reached**
                    
                    You've hit the limit for the free Gemini API. 
                    - **Wait**: Free quota resets daily.
                    - **Reduce Batch Size**: Try filtering your data in Tab 1 to fewer users.
                    - **Upgrade**: Consider adding billing in Google Cloud for higher throughput.
                    """)
                    return "Error: API quota exceeded. Please try smaller batches or wait."
            
            # Handle other specific errors
            elif "safety" in error_str.lower():
                return "Error: Content flagged by safety filters."
            
            else:
                if attempt < max_retries - 1:
                    st.toast(f"🔄 Error: {error_str}. Retrying...")
                    continue
                st.error(f"Gemini API error: {error_str}")
                return f"Error: {error_str}"
    
    return "Error: Failed to get response after multiple attempts."