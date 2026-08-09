from datetime import datetime, timezone

from database.db import db

class Post(db.Model):
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey("topics.id"), nullable=False)
    content = db.Column(db.Text, nullable=False)
    rationale = db.Column(db.Text, nullable=True)
    sources = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(30), default="draft", nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    published_at = db.Column(db.DateTime, nullable=True)
