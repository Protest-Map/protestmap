from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

class Config:
    """
    Base configuration class for the Flask application.
    """
    SECRET_KEY = os.getenv("SECRET_KEY", "default_key")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql://postgres:admin@localhost:5432/protest_map")
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Recommended to reduce overhead

    # Additional optional configurations
    DEBUG = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")
    TESTING = False


class DevelopmentConfig(Config):
    """
    Development-specific configuration.
    """
    DEBUG = True


class TestingConfig(Config):
    """
    Testing-specific configuration.
    """
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv("TEST_DATABASE_URL", "sqlite:///:memory:")  # Use an in-memory database for testing


class ProductionConfig(Config):
    """
    Production-specific configuration.
    """
    DEBUG = False
    TESTING = False
