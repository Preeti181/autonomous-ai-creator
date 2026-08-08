from flask import Flask

from config import Config
from database.db import db
from routes.health_routes import health_bp
from routes.agent_routes import agent_bp


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)

    app.register_blueprint(health_bp)
    app.register_blueprint(agent_bp)

    with app.app_context():
        db.create_all()

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)