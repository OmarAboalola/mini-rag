from enum import Enum

class LLMEnums(Enum):
    OPENAI = "openai"
    COHERE = "cohere"

class OpenAIEnums(Enum):
    SYSTEM="system"
    ASSISTANT="assistant"
    USER="user"
class CohereEnums(Enum):
    SYSTEM="SYSTEM"
    ASSISTANT="ASSISTANT"
    USER="CHATBOT"
    DOCUMENT="search_document"
    QUERY="search_query"


class DocumentTypeEnum(Enum):
    DOCUMENT="document"
    QUERY="query"
