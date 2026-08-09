from database.db import db
from services.editorial_service import evaluate_topic
from services.publishing_service import create_post


class PipelineService:

    def process_topic(self, topic):
        """
        Topic
        ↓
        Editorial AI
        ↓
        Publish decision
        ↓
        Create post
        """

        # 1. Evaluate topic using Gemini
        editorial_result = evaluate_topic(topic)

        # 2. Reject if AI says not to publish
        if not editorial_result.get("publish", False):
            topic.status = "rejected"
            db.session.commit()

            return {
                "success": False,
                "stage": "editorial",
                "topic_id": topic.id,
                "result": editorial_result,
                "post": None,
            }

        # 3. Create post
        post = create_post(
            topic,
            editorial_result,
        )

        # 4. Safety check
        if post is None:
            return {
                "success": False,
                "stage": "publishing",
                "topic_id": topic.id,
                "result": editorial_result,
                "post": None,
            }

        # 5. Success
        return {
            "success": True,
            "stage": "completed",
            "topic_id": topic.id,
            "result": editorial_result,
            "post": post,
        }


def process_topic(topic):
    service = PipelineService()
    return service.process_topic(topic)