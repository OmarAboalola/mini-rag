from ..LLMInterface import LLMInterface
from ..LLMEnums import CohereEnums
import cohere
import logging

class CohereProvider(LLMInterface):
    def __init__(self, api_key: str,
                 default_input_max_characters: int = 1000,
                 default_generation_max_output: int = 1000,
                 default_generation_temperature: float = 0.1):
        self.api_key = api_key

        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_output = default_generation_max_output
        self.default_generation_temperature = default_generation_temperature

        self.generation_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None

        self.api_client = cohere.ClientV2(api_key=self.api_key)
        self.enums=CohereEnums
        self.logger = logging.getLogger(__name__)

    

    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id

    def set_embedding_model(self, model_id: str, embedding_size: int = None):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size

    def process_text(self, text: str):
        return text[:self.default_input_max_characters].strip() if len(text) > self.default_input_max_characters else text.strip()
    
    def construct_prompt(self, prompt: str, role: str = None):
        return {
            "role": role.lower() if role else "user",
            "content": self.process_text(prompt)
        }
            
    def generate_text(
        self,
        prompt: str,
        chat_history: list = [],
        max_output_tokens: int = None,
        temperature: float = None,
    ):
        if not self.api_client:
            self.logger.error("Cohere client is not initialized.")
            return None

        if not self.generation_model_id:
            self.logger.error("Generation model is not set.")
            return None

        max_output_tokens = (
            max_output_tokens
            if max_output_tokens is not None
            else self.default_generation_max_output
        )

        temperature = (
            temperature
            if temperature is not None
            else self.default_generation_temperature
        )

        try:
            messages = []

            # Add previous chat history if available
            if chat_history:
                messages.extend(chat_history)

            # Add current user prompt
            messages.append(
                {
                    "role": "user",
                    "content": self.process_text(prompt),
                }
            )

            response = self.api_client.chat(
                model=self.generation_model_id,
                messages=messages,
                temperature=temperature,
                max_tokens=max_output_tokens,
            )

            chat_history.append(
                self.construct_prompt(
                    prompt=prompt,
                    role=CohereEnums.USER.value,
                )
            )

            return response.message.content[0].text

        except Exception as e:
            self.logger.exception(e)
            return None



    def embed_text(self, text: str, document_type: str = None):
        if not self.api_client:
            self.logger.error("Cohere client is not initialized.")
            return None

        if not self.embedding_model_id:
            self.logger.error("Embedding model is not set.")
            return None

        input_type = CohereEnums.DOCUMENT.value

        if document_type == CohereEnums.QUERY.value:
            input_type = CohereEnums.QUERY.value

        try:
            response = self.api_client.embed(
                model=self.embedding_model_id,
                texts=[self.process_text(text)],
                input_type=input_type,
                embedding_types=["float"],
            )

            if (
                response is None
                or response.embeddings is None
                or response.embeddings.float is None
                or len(response.embeddings.float) == 0
            ):
                self.logger.error("Failed to get embedding from Cohere API.")
                return None

            return response.embeddings.float[0]

        except Exception as e:
            self.logger.exception(e)
            return None