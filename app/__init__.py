import os
from flask import Flask, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_admin import Admin
from flask_login import LoginManager, current_user
from flask_admin.contrib.sqla import ModelView
from werkzeug.security import generate_password_hash
from app.database import db, init_app as init_db  # Use the correct db and init_app from app.database
from config import Config
from app.models import User


# Initialize extensions
migrate = Migrate()
login_manager = LoginManager()
admin = Admin(template_mode="bootstrap4")

def create_app(config_class=Config):
    """
    Factory function to create and configure the Flask application.

    Returns:
        Flask: The configured Flask application instance.
    """
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config.from_object(config_class)

    # Initialize extensions
    try:
        init_db(app)
    except Exception as e:
        app.logger.exception("Failed to initialize the database.")
        raise
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = lambda: url_for("routes.login")
    admin.init_app(app)

    # Import models AFTER app initialization to avoid circular imports
    with app.app_context():
        from app.models import (
            User, Role, Permission, Marker, Category, Tag, Location, Comment, Media, AuditLog, MarkerAuditLog, DeletedMarker
        )

        # Utility function to avoid duplicate Admin view registration
        def is_view_registered(admin_instance, endpoint_name):
            """Check if a view with the given endpoint is already registered."""
            return any(view.endpoint == endpoint_name for view in admin_instance._views)

        # Custom ModelView for Admin Panel
        class AdminModelView(ModelView):
            def is_accessible(self):
                return current_user.is_authenticated and current_user.role == "admin"

            def inaccessible_callback(self, name, **kwargs):
                return redirect(url_for("routes.login"))

        # Define Admin Views to register
        views_to_register = [
            (User, "admin_user_view", "User Management"),
            (Role, "admin_role_view", "Role Management"),
            (Permission, "admin_permission_view", "Permission Management"),
            (Marker, "admin_marker_view", "Marker Management"),
            (Category, "admin_category_view", "Category Management"),
            (Tag, "admin_tag_view", "Tag Management"),
            (Location, "admin_location_view", "Location Management"),
            (Comment, "admin_comment_view", "Comment Management"),
        ]

        # Safely register Admin Views
        for model, endpoint, name in views_to_register:
            if not is_view_registered(admin, endpoint):
                admin.add_view(AdminModelView(model, db.session, endpoint=endpoint, name=name))

    # Register Blueprints AFTER models and views
    from app.routes import routes_bp
    app.register_blueprint(routes_bp)

    from app.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # Register error handlers
    register_error_handlers(app)

    # Register custom CLI commands
    register_cli_commands(app)

    app.logger.info(f"Registered blueprints: {list(app.blueprints.keys())}")
    return app


def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def internal_error(e):
        app.logger.exception("Internal server error")
        return jsonify({"error": "Internal server error"}), 500

@login_manager.user_loader
def load_user(user_id):
    """
    Required user_loader callback for Flask-Login.
    """
    return db.session.get(User, int(user_id))


def create_default_admin():
    """
    Create a default admin user if it doesn't already exist.
    """
    from app.models import User

    with db.session.begin():
        if not User.query.filter_by(email="admin@example.com").first():
            admin_password = os.environ.get("DEFAULT_ADMIN_PASSWORD", "adminpassword")
            admin_user = User(
                email="admin@example.com",
                name="Admin",
                role="admin",
                password=generate_password_hash(admin_password, method="sha256"),
            )
            db.session.add(admin_user)


def register_cli_commands(app):
    @app.cli.command("create-admin")
    def create_admin():
        create_default_admin()
        print("Admin user created (email: admin@example.com, password set via environment variable or 'adminpassword').")
