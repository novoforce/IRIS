import json
import sys
import os

# Add project root to path if not already added
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from src.agents.base_agent import CustomLlmAgent

from pydantic import BaseModel

class EntityExtractionOutput(BaseModel):
    entities: list[str]
    attributes: list[str]
    reason: str

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
        # Pass the Pydantic model as schema
        response_data = self.get_llm_response(prompt, temperature=0.0, response_schema=EntityExtractionOutput)
        
        # response_data should be a dict (parsed JSON)
        if isinstance(response_data, dict):
             return response_data
        
        # Fallback if something went wrong and we got string
        try:
             import json
             return json.loads(response_data)
        except:
             print(f"Error decoding JSON from EntityExtractionAgent: {response_data}")
             return {"entities": [], "attributes": [], "reason": "Error parsing output"}
