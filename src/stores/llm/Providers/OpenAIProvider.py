from ..LLMInterface import LLMInterface
from openai import OpenAI
import logging
from ..LLMEnums import OPENAIModel

class OpenAiProvider(LLMInterface):
    def __init__(self, api_key: str,api_url: str = None,
                default_input_max_characters: int = 1000, 
                default_generation_max_output: int = 1000,
                default_generation_temperature: float = 0.1):
        self.api_key=api_key
        self.api_url=api_url

        self.default_input_max_characters=default_input_max_characters
        self.default_generation_max_output=default_generation_max_output
        self.default_generation_temperature=default_generation_temperature

        self.generation_model_id = None
        self.embedding_model_id = None
        self.embedding_model_id = None

        self.api_client = OpenAI(api_key=self.api_key, api_url=self.api_url) 
        self.logger = logging.getLogger(__name__)

    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id
        self.logger.info(f"Generation model set to: {model_id}")
    
    def set_embedding_model(self, model_id: str, embedding_size: int = None):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size
        self.logger.info(f"Embedding model set to: {model_id}")


    def process_text(self, text: str):
        return text[:self.default_input_max_characters].strip() if len(text) > self.default_input_max_characters else text


    def generate_text(self, prompt: str, chat_history: list = [], max_output_tokens: int = None,
                      temperature: float = None):
        if not self.client:
            self.logger.error("OpenAI client is not initialized. Please check your API key and URL.")
        if not self.generation_model_id:
            self.logger.error("Generation model is not set. Please set it using set_generation_model")
        max_output_tokens=max_output_tokens if max_output_tokens is not None else self.default_generation_max_output       
        temperature=temperature if temperature is not None else self.default_generation_temperature

        chat_history.append(self.construct_prompt(prompt=prompt, role=OPENAIModel.USER.value))

        response = self.api_client.chat.completions.create(
            model=self.generation_model_id,
            messages=chat_history,
            max_tokens=max_output_tokens,
            temperature=temperature
        )

        if not response or not respose.choices or  len(response.choices) == 0 or  not response.choices[0].message:
            self.logger.error("Failed to get response from OpenAI API.")
            return None
        return response.choices[0].message["content"]
    
    def embedd_text(self, text: str, document_type: str=None):
        if not self.client:
            self.logger.error("OpenAI client is not initialized. Please check your API key and URL.")
        if not self.embedding_model_id:
            self.logger.error("Embedding model is not set. Please set it using set_embedding_model")
        
        response = self.api_client.embeddings.create(model=self.embedding_model_id,
                                                     input=text)
        if not response or 'data' not in response or len(response['data']) == 0 or response['data'][0].embedding is None:
            self.logger.error("Failed to get embedding from OpenAI API.")
            return None
        return response['data'][0].embedding
    
    def construct_prompt(self, prompt: str, role: str = None):
       return {
           "role": role,
           "content": self.process_text(prompt)
       }
        

