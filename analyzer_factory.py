import os
from dotenv import load_dotenv
from src.ai_analyzer.mistral_client import MistralAnalyzer
from src.ai_analyzer.anthropic_client import AnthropicAnalyzer
from src.ai_analyzer.openai_client import OpenAIAnalyzer

load_dotenv()

class AnalyzerFactory:
    def __init__(self):
        self.available_models = []
        self._load_available_models()

    def _load_available_models(self):
        if os.getenv("MISTRAL_API_KEY"):
            self.available_models.append("Mistral")
        if os.getenv("ANTHROPIC_API_KEY"):
            self.available_models.append("Anthropic")
        if os.getenv("OPENAI_API_KEY"):
            self.available_models.append("OpenAI")

    def get_available_models(self):
        return self.available_models

    def create_analyzer(self, model_name):
        if model_name == "Mistral":
            return MistralAnalyzer()
        elif model_name == "Anthropic":
            return AnthropicAnalyzer()
        elif model_name == "OpenAI":
            return OpenAIAnalyzer()
        else:
            raise ValueError(f"Modelo não suportado: {model_name}")