import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Config:
    # Security
    # SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")

    # Database
    DB_PATH = os.environ.get(
        "DB_PATH",
        os.path.join(BASE_DIR, "ams.db")
    )

    # Uploads
    UPLOAD_FOLDER = os.environ.get(
        "UPLOAD_FOLDER",
        os.path.join(BASE_DIR, "static", "uploads")
    )

    # File upload rules
    ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}

    # Max upload size (5 MB)
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024




class DevelopmentConfig(Config):
    DEBUG = True
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")


class ProductionConfig(Config):
    DEBUG = False
    SECRET_KEY = os.environ.get("SECRET_KEY")

    @classmethod
    def validate(cls):
        if not cls.SECRET_KEY:
            raise RuntimeError(
                "SECRET_KEY environment variable must be set in production"
            )

