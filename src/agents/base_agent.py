import os
import yaml
from google import genai
from google.genai import types
from typing import Any, Dict, Optional
from dotenv import load_dotenv
from pydantic import ConfigDict

# Import ADK classes
from google.adk.agents import LlmAgent, BaseAgent as AdkBaseAgent

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '../../secrets/.env'))

class BaseAgentWrapper:
    """
    Mixin/Helper for common logic like config loading.
    """
    def setup_wrapper(self, agent_name: str, config: Optional[Dict[str, Any]] = None):
        self._wrapper_agent_name = agent_name
        self._config = config if config is not None else self._load_config_static(agent_name)
        self._setup_llm()

    @property
    def config(self) -> Dict[str, Any]:
        return self._config

    @staticmethod
    def _load_config_static(agent_name: str) -> Dict[str, Any]:
        """Loads the YAML configuration for the specific agent."""
        config_path = os.path.join(os.path.dirname(__file__), agent_name, 'config.yaml')
        if not os.path.exists(config_path):
            return {}
        with open(config_path, 'r') as file:
            return yaml.safe_load(file)

    def load_config(self, agent_name: str) -> Dict[str, Any]:
        return self._load_config_static(agent_name)

    def _setup_llm(self):
        """Sets up the Gemini LLM client (v2)."""
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            self._client = genai.Client(api_key=api_key)
            self._model_name = self._config.get('llm_model', 'gemini-1.5-flash-latest') # Updated model name format often preferred in v2? or just use full resource name.
            # Using standard model names.

    def get_llm_response(self, prompt: str, temperature: float = 0.0, response_schema: Any = None) -> Any:
        """Generates a response from the LLM (v2)."""
        generation_config = types.GenerateContentConfig(
            temperature=temperature
        )
        
        if response_schema:
            generation_config.response_mime_type = "application/json"
            generation_config.response_schema = response_schema

        response = self._client.models.generate_content(
            model=self._model_name,
            contents=prompt,
            config=generation_config
        )
        
        if response_schema:
            # If schema is provided, response.text is a JSON string.
            # Using parsed (if available) or manual load might be needed depending on SDK version.
            # safe assumption: usage of json.loads if not automatically parsed.
            import json
            try:
                # With v2 SDK, it should return a JSON string in .text
                # Sometimes .parsed is available if typed dict is used?
                # For safety, let's try to return parsed object if schema was requested.
                return json.loads(response.text)
            except Exception as e:
                print(f"Error parsing structured response: {e}, text: {response.text}")
                return response.text
                
        return response.text

class CustomLlmAgent(LlmAgent, BaseAgentWrapper):
    model_config = ConfigDict(extra='allow')
    
    def __init__(self, agent_name: str):
        # Load config first for arguments
        cfg = BaseAgentWrapper._load_config_static(agent_name)
        instruction = cfg.get('prompt_template', f"You are {agent_name}")
        model_name = cfg.get('llm_model', 'models/gemini-1.5-flash') # Default fallback
        
        super().__init__(
            name=agent_name,
            model=model_name,
            instruction=instruction
        )
        # Restore wrapper state
        self.setup_wrapper(agent_name, config=cfg)

class CustomBaseAgent(AdkBaseAgent, BaseAgentWrapper):
    model_config = ConfigDict(extra='allow')

    def __init__(self, agent_name: str):
        super().__init__(name=agent_name)
        self.setup_wrapper(agent_name)
