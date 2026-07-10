from enum import Enum

class LLMModelType(Enum):
    OPENAI = "openai"
    COHERE = "cohere"

class OPENAIModel(Enum):
    SYSTEM="system"
    ASSISTANT="assistant"
    USER="user"