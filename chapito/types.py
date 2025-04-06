from enum import Enum


class OsType(Enum):
    UNKNOWN = 0
    WINDOWS = 1
    LINUX = 2
    MACOS = 3


class Chatbot(Enum):
    GROK = "grok"
    MISTRAL = "mistral"
    PERPLEXITY = "perplexity"
    OPENAI = "openai"
    GEMINI = "gemini"
    DEEPSEEK = "deepseek"
    ANTHROPIC = "anthropic"
    GITHUB = "github"
    DUCKDUCKGO = "duckduckgo"
    INCEPTIONLABS = "inceptionlabs"
