from google.adk.agents import LlmAgent
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load Env for API Key
load_dotenv('secrets/.env')
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

try:
    print("Creating Agent...")
    agent = LlmAgent(
        name="test_agent",
        model="models/gemini-flash-latest", # Use the working model
        instruction="You are a helpful assistant. Reply with 'Pong' if I say 'Ping'."
    )
    
    input_text = "Ping"
    print(f"Input: {input_text}")
    
    # Try different methods
    # Method 1: __call__
    try:
        print("\nAttempting __call__...")
        res = agent(input_text)
        print(f"__call__ result: {res}")
    except Exception as e:
        print(f"__call__ failed: {e}")

    # Method 2: run
    try:
        print("\nAttempting .run()...")
        res = agent.run(input_text)
        print(f".run() result: {res}")
    except Exception as e:
        print(f".run() failed: {e}")

    # Method 3: process
    try:
        print("\nAttempting .process()...")
        res = agent.process(input_text)
        print(f".process() result: {res}")
    except Exception as e:
        print(f".process() failed: {e}")

except Exception as e:
    print(f"Setup failed: {e}")
