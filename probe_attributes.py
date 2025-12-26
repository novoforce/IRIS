from google.adk.agents import LlmAgent
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv('secrets/.env')
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

try:
    agent = LlmAgent(
        name="test_agent",
        model="models/gemini-flash-latest",
        instruction="Reply 'Pong'"
    )
    
    print("Agent attributes:", dir(agent))
    
    # Check if 'model' attribute is the generative model or string
    # print("Agent model:", agent.model) 
    
except Exception as e:
    print(f"Error: {e}")
