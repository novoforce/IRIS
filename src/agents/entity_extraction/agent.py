import json
import sys
import os

# Add project root to path if not already added
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from src.agents.base_agent import BaseAgent

class EntityExtractionAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_name="entity_extraction")

    def execute(self, user_query: str) -> dict:
        """
        Extracts entities from the user query.
        
        Args:
            user_query (str): The natural language query from the user.
            
        Returns:
            dict: A dictionary containing extracted entities, attributes, and timeframe.
        """
        prompt = self.config['prompt_template'].format(user_query=user_query)
        response_text = self.get_llm_response(prompt, temperature=0.0)
        
        # Clean the response to ensure it's valid JSON
        # Sometimes LLMs add backticks or 'json' prefix
        cleaned_text = response_text.replace('```json', '').replace('```', '').strip()
        
        try:
            return json.loads(cleaned_text)
        except json.JSONDecodeError:
            print(f"Error decoding JSON from EntityExtractionAgent: {response_text}")
            # Fallback or empty return
            return {"entities": [], "attributes": [], "timeframe": None}
