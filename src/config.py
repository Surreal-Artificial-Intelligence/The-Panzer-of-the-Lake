SUPPORTED_MODELS = {
    "Azure": [
        "gpt-3.5-turbo",
        "gpt-4o",
    ],
    "OpenAI": [
        "gpt-3.5-turbo",
        "gpt-4o",
    ],
    "Cohere": [
        "command-r-plus",
    ],
    "Ollama": [
        "mistral",
        "samantha-mistral",
        "aya",
    ],
}


CHATS_PATH = "./chats"
TEMPLATES_PATH = "./templates"
ASSETS_PATH = "./assets"
DB_PATH = "./db/db.json"

LOGO_CONFIG = {
    "image": f"{ASSETS_PATH}/surreal-logo-and-text.png",
    "icon_image": f"{ASSETS_PATH}/surreal-logo.jpg"
}
