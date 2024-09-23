SUPPORTED_MODELS = {
    "Azure": [
        "gpt-4o",
        "gpt-4o-mini",
    ],
    "OpenAI": [
        "gpt-4o",
        "gpt-4o-mini",
    ],
    "Cohere": [
        "command-r-plus",
    ],
    "TogetherAI": [
        "NousResearch/Hermes-3-Llama-3.1-405B-Turbo",
    ],
    "Ollama": ["mistral", "samantha-mistral", "aya", "bakllava"],
}

models = {
    "Azure": [
        {"model_name": "gpt-3.5-turbo", "context_length": 32000},
        {"model_name": "gpt-4o", "context_length": 128000},
    ],
    "OpenAI": [
        {"model_name": "gpt-3.5-turbo", "context_length": 32000},
        {"model_name": "gpt-4o", "context_length": 128000},
        {"model_name": "gpt-4o-mini", "context_length": 65000},
    ],
    "Cohere": [
        {"model_name": "command-r-plus", "context_length": 128000},
    ],
    "Ollama": [{"model_name": "aya", "context_length": 16000}],
    "Meta": [
        {"model_name": "Meta-Llama-3.1-8B-Instruct-Turbo", "context_length": 131072},
        {"model_name": "Meta-Llama-3.1-70B-Instruct-Turbo", "context_length": 131072},
        {"model_name": "Meta-Llama-3.1-405B-Instruct-Turbo", "context_length": 8192},
    ],
    "MistralAI": [
        {"model_name": "Mistral-7B-Instruct-v0.3", "context_length": 32768},
        {"model_name": "Mixtral-8x22B-Instruct-v0.1", "context_length": 65536},
    ],
    "NousResearch": [
        {"model_name": "Hermes-3-Llama-3.1-405B-Turbo", "context_length": 8192},
        {"model_name": "NousResearch-9x5B-Instruct-v0.4", "context_length": 65536},
    ],
}

OPENAI = "openai"
AZURE = "azure"
MISTRALAI = "mistralai"
META = "meta-llama"
MICROSOFT = "microsoft"
GOOGLE = "google"
NOUSRESEARCH = "NousResearch"
QWEN = "Qwen"
TOGETHER = "togethercomputer"
UPSTAGE = "upstage"
GRYPHE = "gryphe"
DEEPSEEK = "deepseek-ai"
DATABRICKS = "databricks"


CHATS_PATH = "./chats"
TEMPLATES_PATH = "./templates"
ASSETS_PATH = "./assets"
DB_PATH = "./db"

LOGO_CONFIG = {"image": f"{ASSETS_PATH}/surreal-logo-and-text.png", "icon_image": f"{ASSETS_PATH}/surreal-logo.jpg"}
