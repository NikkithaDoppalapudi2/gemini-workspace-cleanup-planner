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

    # List of models to try in order of preference
    # Using full model names with prefixes as returned by list_models()
    models_to_try = [
        'models/gemini-1.5-flash',
        'models/gemini-pro',
        'gemini-1.5-flash',
        'gemini-pro'
    ]
    
    last_error = ""
    
    for model_name in models_to_try:
        try:
            # Re-configure to ensure fresh state if needed
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model_name)
            
            for attempt in range(max_retries):
                try:
                    # Exponential backoff with jitter
                    if attempt > 0:
                        wait_time = (2 ** attempt) + random.uniform(0, 1)
                        time.sleep(wait_time)
                    
                    response = model.generate_content(prompt)
                    
                    if response.candidates:
                        candidate = response.candidates[0]
                        if candidate.content.parts:
                            return candidate.content.parts[0].text
                        else:
                            # If blocked by safety, we can't do much with this model/prompt
                            return "Error: Empty response. Safety filters might be blocking the output."
                    else:
                        return "Error: No response generated. Safety filters might be blocking the output."
                
                except Exception as e:
                    error_str = str(e)
                    last_error = error_str
                    
                    # If quota/rate limit error, retry with backoff
                    if any(indicator in error_str.lower() for indicator in ["429", "resource_exhausted", "quota", "too many requests"]):
                        if attempt < max_retries - 1:
                            st.toast(f"⏳ Rate limit hit for {model_name}. Retrying... ({attempt+1}/{max_retries})")
                            continue
                        else:
                            # Quota exhausted for this model, try next model in list
                            break 
                    
                    # If model not found (404), try next model immediately
                    elif "404" in error_str or "not found" in error_str.lower():
                        break
                    
                    else:
                        # Other error, try next attempt
                        if attempt < max_retries - 1:
                            continue
                        break
            
            # If we successfully got a response (returning above), we're done
            # If we're here, it means we exhausted retries or broke out to try next model
            
        except Exception as e:
            last_error = str(e)
            continue

    # Final error handling if all models/retries fail
    if any(indicator in last_error.lower() for indicator in ["429", "resource_exhausted", "quota", "too many requests"]):
        st.error("🚫 Gemini API Quota Exceeded")
        st.warning("""
        **Free Tier Limit Reached**
        - **Wait**: Free quota resets daily.
        - **Batching**: Try analyzing fewer users at once (use filters in the first tab).
        """)
        return "Error: API quota exceeded. Please try smaller batches later."
    else:
        st.error(f"Gemini API error: {last_error}")
        return f"Error: {last_error}"