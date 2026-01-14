from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

client = genai.Client()

def call_gemini(prompt):
    response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
    return response.text