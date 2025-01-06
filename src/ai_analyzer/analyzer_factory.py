from typing import List

class AnalyzerFactory:
    @staticmethod
    def create_analyzer(analyzer_type: str):
        """Cria uma instância do analisador baseado no tipo."""
        if analyzer_type == "gpt-3.5-turbo":
            from .openai_client import OpenAIAnalyzer
            return OpenAIAnalyzer()
        elif analyzer_type == "claude-3-opus":
            from .anthropic_client import AnthropicAnalyzer
            return AnthropicAnalyzer()
        elif analyzer_type == "mixtral-8x7b":
            from .mixtral_client import MixtralAnalyzer
            return MixtralAnalyzer()
        else:
            raise ValueError(f"Tipo de analisador desconhecido: {analyzer_type}")

    @staticmethod
    def get_available_models() -> List[str]:
        """Retorna uma lista dos modelos disponíveis."""
        return ["gpt-3.5-turbo", "claude-3-opus", "mixtral-8x7b"]

    @staticmethod
    def create_analyzer_by_model_name(model_name: str):
        if model_name == "gpt-3.5-turbo":
            from .openai_client import OpenAIAnalyzer
            return OpenAIAnalyzer()
        elif model_name == "claude-3-opus":
            from .anthropic_client import AnthropicAnalyzer
            return AnthropicAnalyzer()
        elif model_name == "mixtral-8x7b":
            from .mixtral_client import MixtralAnalyzer
            return MixtralAnalyzer()
        else:
            raise ValueError(f"Modelo não suportado: {model_name}")