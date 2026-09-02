from enum import Enum


class EmbeddingProviderType(str, Enum):
    LOCAL = "local"
    REMOTE = "remote"


class LLMProviderType(str, Enum):
    GEMINI = "gemini"


class VectorDBProviderType(str, Enum):
    QDRANT = "qdrant"


class DocumentParserType(str, Enum):
    LOCAL = "local"
    REMOTE = "remote"


class STTProviderType(str, Enum):
    GROQ = "groq"

