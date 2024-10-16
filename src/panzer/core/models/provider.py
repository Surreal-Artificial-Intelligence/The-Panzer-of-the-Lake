from enum import Enum


class Provider(Enum):
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
