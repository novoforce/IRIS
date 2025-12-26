from google.adk.agents import LlmAgent
import google.generativeai as genai
import os

try:
    print("Attempting to instantiate LlmAgent...")
    # Guessing parameters based on standard practices
    agent = LlmAgent(
        name="test_agent",
        model="gemini-pro",
        instruction="You are a test agent."
    )
    print("Success with name, model, instruction")
    print(agent)
except Exception as e:
    print(f"Failed: {e}")

try:
    print("\nAttempting with system_prompt...")
    agent = LlmAgent(
        name="test_agent_2",
        model="gemini-pro",
        system_prompt="You are a test agent."
    )
    print("Success with system_prompt")
except Exception as e:
    print(f"Failed: {e}")
