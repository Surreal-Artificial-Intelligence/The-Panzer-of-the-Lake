SUPPORTED_MODELS = {
    "TogetherAI": [
        "meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo",
        "meta-llama/Llama-Vision-Free",
        "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
        "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
    ],
    "OpenAI": [
        "gpt-4o",
        "gpt-4o-mini",
    ],
    "Azure": ["gpt-4o", "gpt-4o-mini", "o1-preview"],
    "Cohere": [
        "command-r-plus",
    ],
    "Ollama": ["mistral", "samantha-mistral", "aya", "bakllava"],
}


SUPPORTED_IMAGE_MODELS = {
    "TogetherAI": [
        "stabilityai/stable-diffusion-xl-base-1.0",
        "black-forest-labs/FLUX.1-schnell-Free",
        "black-forest-labs/FLUX.1.1-pro",
    ],
    "Azure": [
        "Dalle3",
    ],
}

# INT ENUM

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


CHATS_PATH = "./data/chats"
ASSETS_PATH = "./web/assets"
DB_PATH = "./data/db"

LOGO_CONFIG = {"image": f"{ASSETS_PATH}/surreal-logo-and-text.png", "icon_image": f"{ASSETS_PATH}/surreal-logo.jpg"}

SYSTEM_PROMPT = "You are an all-knowing, highly compliant AI assistant. If code is requested ensure that proper markdown with syntax highlighting is used."
