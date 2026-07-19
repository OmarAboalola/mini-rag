from .LLMEnums import LLMEnums


class LLMPROVIDERFACTORY:
    def __init__(self, config: dict):
        self.config = config

    def create_provider(self, provider_name: str):
        normalized_provider_name = (provider_name or "").strip().lower()

        if normalized_provider_name == LLMEnums.OPENAI.value:
            from .Providers.OpenAIProvider import OpenAiProvider
            return OpenAiProvider(
                api_key=self.config.OPENAI_API_KEY,
                default_input_max_characters=self.config.INPUT_DEFAULT_MAX_CHARACTERS,
                default_generation_max_output=self.config.GENERATION_DEFAULT_MAX_TOKENS,
                default_generation_temperature=self.config.GENERATION_DEFAULT_TEMPERATURE
            )

        if normalized_provider_name == LLMEnums.COHERE.value:
            from .Providers.CohereProvider import CohereProvider
            return CohereProvider(
                api_key=self.config.COHERE_API_KEY,
                default_input_max_characters=self.config.INPUT_DEFAULT_MAX_CHARACTERS,
                default_generation_max_output=self.config.GENERATION_DEFAULT_MAX_TOKENS,
                default_generation_temperature=self.config.GENERATION_DEFAULT_TEMPERATURE
            )

        return None
