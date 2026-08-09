from flask import Flask, send_from_directory

from config import Config
from database.db import db
from routes.health_routes import health_bp
from routes.agent_routes import agent_bp
from scheduler.autonomous_scheduler import start_scheduler

from pathlib import Path


def create_app():
    """Create and configure Flask application."""

    app = Flask(__name__)

    # CORS
    @app.after_request
    def add_cors_headers(response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        return response

    # Configuration
    app.config.from_object(Config)

    # Database
    db.init_app(app)

    # Routes
    app.register_blueprint(health_bp)
    app.register_blueprint(agent_bp)

    # Create database tables
    with app.app_context():
        db.create_all()

    # Serve frontend
    frontend_dir = Path(__file__).resolve().parent.parent / "frontend" / "web"

    @app.route("/")
    def home():
        return send_from_directory(str(frontend_dir), "index.html")

    @app.route("/dashboard")
    def dashboard():
        return send_from_directory(str(frontend_dir), "index.html")

    return app


app = create_app()


if __name__ == "__main__":
    start_scheduler(app)

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
        use_reloader=False
    )
# ============================================================
# DATABASE INITIALIZATION
# ============================================================

try:
    with app.app_context():
        from database.db import db
        db.create_all()
        print("✅ Database tables initialized successfully")
except Exception as e:
    print(f"⚠️ Database initialization warning: {e}")