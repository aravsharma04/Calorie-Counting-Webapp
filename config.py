import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "super-secret-key-change-me"
    SQLALCHEMY_DATABASE_URI = "sqlite:///tracker.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
