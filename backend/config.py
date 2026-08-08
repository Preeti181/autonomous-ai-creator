import os


class Config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///autonomous_ai.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "development-secret-key"
    )