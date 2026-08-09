from models.topic import Topic
from database.db import db


def select_topics(limit=5, minimum_score=20):
    """
    Select the highest-scoring topics for content creation.

    Only topics with status='scored' and a score greater than
    or equal to minimum_score are considered.
    """

    topics = (
        Topic.query
        .filter(
            Topic.status == "scored",
            Topic.score >= minimum_score
        )
        .order_by(Topic.score.desc())
        .limit(limit)
        .all()
    )

    selected_topics = []

    for topic in topics:
        topic.status = "selected"
        topic.reason = (
            f"Selected for content creation because "
            f"its relevance score is {topic.score}."
        )

        selected_topics.append(topic)

    db.session.commit()

    return selected_topics