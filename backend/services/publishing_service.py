import json
from datetime import datetime, timezone

from database.db import db
from models.post import Post
from utils.source_cleaner import clean_sources


class PublishingService:

    def create_post(self, topic, editorial_result):
        if not editorial_result.get("publish"):
            return None

        content = editorial_result.get("text", "").strip()

        if not content:
            return None

        sources = clean_sources(
            editorial_result.get("sources", [])
        )

        post = Post(
            topic_id=topic.id,
            content=content,
            rationale=editorial_result.get("rationale", "").strip(),
            sources=json.dumps(sources),
            status="draft",
            created_at=datetime.now(timezone.utc),
        )

        db.session.add(post)

        topic.status = "draft"

        db.session.commit()

        return post


def create_post(topic, editorial_result):
    service = PublishingService()
    return service.create_post(topic, editorial_result)
