# app/blueprints/__init__.py

from app.blueprints.auth import auth_bp
from app.blueprints.routes import routes_bp

# Expose these blueprints for easy imports
__all__ = ["auth_bp", "routes_bp"]
