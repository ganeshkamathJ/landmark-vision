"""
Landmark Vision — Flask Application Factory
"""
import os
from flask import Flask
from config import config


def create_app(env="development"):
    # Ensure we run from the project root so relative paths (e.g., uploads) resolve correctly
    import os
    os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
    )
    app.config.from_object(config[env])

    # Ensure upload folder exists
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Initialize SQLite database
    from app.db import init_db
    init_db()

    # Register blueprints
    from app.routes import main
    app.register_blueprint(main)

    return app
