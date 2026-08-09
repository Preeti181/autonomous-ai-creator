from datetime import datetime, timezone

from database.db import db


class Topic(db.Model):
    __tablename__ = "topics"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    source = db.Column(db.String(200), nullable=False)
    url = db.Column(db.String(1000), nullable=False, unique=True)
    score = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(30), default="discovered", nullable=False)
    reason = db.Column(db.Text, nullable=True)
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    