import os
import yaml
import google.generativeai as genai
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '../../secrets/.env'))

class BaseAgent(ABC):
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.config = self.load_config()
        self._setup_llm()

    def load_config(self) -> Dict[str, Any]:
        """Loads the YAML configuration for the specific agent."""
        config_path = os.path.join(os.path.dirname(__file__), self.agent_name, 'config.yaml')
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found for agent {self.agent_name} at {config_path}")
        
        with open(config_path, 'r') as file:
            return yaml.safe_load(file)

    def _setup_llm(self):
        """Sets up the Gemini LLM client."""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables.")
        
        genai.configure(api_key=api_key)
        
        model_name = self.config.get('llm_model', 'gemini-pro')
        self.model = genai.GenerativeModel(model_name)

    def get_llm_response(self, prompt: str, temperature: float = 0.0) -> str:
        """Generates a response from the LLM."""
        response = self.model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=temperature
            )
        )
        return response.text

    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """Abstract method to define the agent's main logic."""
        pass
