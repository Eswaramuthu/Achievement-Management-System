import os

# =====================================================
# 🔹 Base directory
# =====================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# =====================================================
# 🔹 Base Configuration
# =====================================================
class Config:
    """
    Base configuration:
    - Security
    - Database
    - Uploads
    - File rules
    """

    # Secret key (commented in base, set in Dev/Prod)
    # SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")

    # Database path
    DB_PATH = os.environ.get(
        "DB_PATH",
        os.path.join(BASE_DIR, "ams.db")
    )

    # Upload folder
    UPLOAD_FOLDER = os.environ.get(
        "UPLOAD_FOLDER",
        os.path.join(BASE_DIR, "static", "uploads")
    )

    # Allowed file extensions for uploads
    ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}

    # Maximum upload size (5 MB)
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024


# =====================================================
# 🔹 Development Configuration
# =====================================================
class DevelopmentConfig(Config):
    DEBUG = True
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")


# =====================================================
# 🔹 Production Configuration
# =====================================================
class ProductionConfig(Config):
    DEBUG = False
    SECRET_KEY = os.environ.get("SECRET_KEY")

    @classmethod
    def validate(cls):
        """Ensure SECRET_KEY is set in production."""
        if not cls.SECRET_KEY:
            raise RuntimeError(
                "SECRET_KEY environment variable must be set in production!"
            )
