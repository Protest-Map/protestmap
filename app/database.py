# app/database.py
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base

# Initialize the SQLAlchemy database instance with the custom Base
db = SQLAlchemy()

# Define the base class for your models
Base = declarative_base()  # Base for models

# Optional: Convenience function to initialize the database with the Flask app
def init_app(app):
    """
    Initialize the SQLAlchemy database with the Flask app.

    Args:
        app: The Flask application instance.
    """
    db.init_app(app)
