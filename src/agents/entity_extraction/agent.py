import json
import sys
import os

# Add project root to path if not already added
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from src.agents.base_agent import CustomLlmAgent

class EntityExtractionAgent(CustomLlmAgent):
    def __init__(self):
        super().__init__(agent_name="entity_extraction")

    def execute(self, user_query: str) -> dict:
        """
        Extracts entities from the user query.
        """
        # We use the prompt template from config, formatted with user_query
        prompt = self.config['prompt_template'].format(user_query=user_query)
        
        # We can use the helper get_llm_response since we are a CustomLlmAgent
        response_text = self.get_llm_response(prompt, temperature=0.0)
        
        cleaned_text = response_text.replace('```json', '').replace('```', '').strip()
        
        try:
            return json.loads(cleaned_text)
        except json.JSONDecodeError:
            print(f"Error decoding JSON from EntityExtractionAgent: {response_text}")
            return {"entities": [], "attributes": [], "timeframe": None}
