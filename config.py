import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def _load_dotenv():
    """Read .env file manually — no extra package needed."""
    env_path = os.path.join(BASE_DIR, ".env")
    if not os.path.exists(env_path):
        return
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            os.environ.setdefault(key, val)   # don't override real env vars


_load_dotenv()


class Config:
    # ── Security ──────────────────────────────────────────────────────────────
    SECRET_KEY = os.environ.get("SECRET_KEY", "landmark-vision-secret-key-2024")

    # ── Upload settings ───────────────────────────────────────────────────────
    UPLOAD_FOLDER      = os.path.abspath(os.path.join(BASE_DIR, "uploads"))
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024          # 16 MB
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif"}

    # ── Model settings ────────────────────────────────────────────────────────
    MODEL_PATH           = os.path.join(BASE_DIR, "model", "landmark_model.h5")
    IMAGE_SIZE           = (224, 224)
    CONFIDENCE_THRESHOLD = 0.30

    # ── API keys  (loaded from .env or real environment variables) ────────────
    # Priority: Keras model → HuggingFace (FREE) → Google Vision → OpenAI → Demo
    HUGGINGFACE_TOKEN     = os.environ.get("HUGGINGFACE_TOKEN", "")
    GOOGLE_VISION_API_KEY = os.environ.get("GOOGLE_VISION_API_KEY", "")
    OPENAI_API_KEY        = os.environ.get("OPENAI_API_KEY", "")

    # ── App settings ──────────────────────────────────────────────────────────
    DEBUG = os.environ.get("FLASK_DEBUG", "False").lower() == "true"


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    "development": DevelopmentConfig,
    "production":  ProductionConfig,
    "default":     DevelopmentConfig,
}
