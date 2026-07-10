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

        self.api_client = cohere.Client(api_key=self.api_key)
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
           "role": role,
           "text": self.process_text(prompt)
       }
    
          
    def generate_text(self, prompt: str, chat_history: list = [], max_output_tokens: int = None,
                      temperature: float = None):
        
        if not self.api_client:
            self.logger.error("Cohere client is not initialized. Please check your API key.")
            return None
        if not self.generation_model_id:
            self.logger.error("Generation model is not set. Please set it using set_generation_model")
            return None
        
        response= self.client.chat(
            model=self.generation_model_id,
            chat_history = chat_history,
            message = self.process_text(prompt)
        )

        max_output_tokens = max_output_tokens if max_output_tokens is not None else self.default_generation_max_output       
        temperature = temperature if temperature is not None else self.default_generation_temperature

        chat_history.append(self.construct_prompt(prompt=prompt, role=CohereEnums.USER.value))

        response = self.api_client.generate(
            model=self.generation_model_id,
            prompt=chat_history,
            max_tokens=max_output_tokens,
            temperature=temperature,
            max_tokens =max_output_tokens,
        )

        if not response or not response.text:
            self.logger.error("Failed to get response from Cohere API.")
            return None
        return response.text
    def embedd_text(self, text: str, document_type: str=None):
        if not self.api_client:
            self.logger.error("Cohere client is not initialized. Please check your API key.")
            return None
        
        if not self.embedding_model_id:
            self.logger.error("Embedding model is not set. Please set it using set_embedding_model")
            return None
        
        input_type = CohereEnums.DOCUMENT
        if document_type == CohereEnums.QUERY: 
            input_type = CohereEnums.QUERY

        
        response = self.api_client.embed(
            model=self.embedding_model_id,
            texts=[self.process_text(text)],
            intput_type=input_type,
            embedding_types=[float], 
        )

        if not response or not response.embeddings or len(response.embeddings) == 0 or not response.embeddings.float :
            self.logger.error("Failed to get embedding from Cohere API.")
            return None
        return  response.embeddings.float[0]
    

    