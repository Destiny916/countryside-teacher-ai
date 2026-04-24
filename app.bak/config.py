import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "SQLALCHEMY_DATABASE_URI",
        f"sqlite:///{BASE_DIR / 'data' / 'user_data.db'}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    VLLM_HOST = os.getenv("VLLM_HOST", "localhost")
    VLLM_PORT = int(os.getenv("VLLM_PORT", "8000"))
    VLLM_MODEL_PATH = os.getenv("VLLM_MODEL_PATH", str(BASE_DIR / "models" / "qwen-7b"))
    VLLM_MODEL_NAME = os.getenv("VLLM_MODEL_NAME", "qwen-7b")

    ASR_MODEL_PATH = os.getenv("ASR_MODEL_PATH", str(BASE_DIR / "models" / "sensevoice"))
    TTS_MODEL_PATH = os.getenv("TTS_MODEL_PATH", str(BASE_DIR / "models" / "cosyvoice"))

    KNOWLEDGE_BASE_DIR = BASE_DIR / "knowledge_base"
    CHROMA_DB_PATH = KNOWLEDGE_BASE_DIR / "chroma_db"

    TEXTBOOK_EDITION = os.getenv("TEXTBOOK_EDITION", "pep")
    MAX_CONCURRENT_USERS = int(os.getenv("MAX_CONCURRENT_USERS", "30"))
    SESSION_TIMEOUT = int(os.getenv("SESSION_TIMEOUT", "3600"))
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", str(16 * 1024 * 1024)))

    DEFAULT_BACKEND = os.getenv("DEFAULT_BACKEND", "remote_nvidia")

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://integrate.api.nvidia.com/v1")
    NVIDIA_MODEL = os.getenv("NVIDIA_MODEL", "z-ai/glm-5.1")

    ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY", "")
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
    QIANFAN_API_KEY = os.getenv("QIANFAN_API_KEY", "")
    QIANFAN_SECRET_KEY = os.getenv("QIANFAN_SECRET_KEY", "")
