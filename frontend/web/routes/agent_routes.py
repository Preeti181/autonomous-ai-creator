from flask import Blueprint, request, jsonify

from database.db import db
from models.post import Post
from models.topic import Topic


agent_bp = Blueprint(
    "agent",
    __name__,
    url_prefix="/api/agent"
)


@agent_bp.route("/init", methods=["POST"])
def init_agent():

    data = request.get_json(silent=True) or {}

    persona = data.get("persona")

    if not persona:
        return jsonify({
            "success": False,
            "error": "persona is required"
        }), 400

    return jsonify({
        "success": True,
        "message": "Agent initialized successfully",
        "persona": persona
    })


@agent_bp.route("/feed", methods=["GET"])
def get_feed():

    try:
        posts = (
            Post.query
            .order_by(Post.id.desc())
            .limit(20)
            .all()
        )

        result = []

        for post in posts:

            topic = None

            if post.topic_id:
                topic = Topic.query.get(post.topic_id)

            result.append({
                "id": post.id,
                "title": topic.title if topic else "AI Generated Post",
                "content": post.content,
                "rationale": post.rationale,
                "status": post.status,
                "sources": post.sources,
                "created_at": (
                    post.created_at.isoformat()
                    if post.created_at
                    else None
                )
            })

        return jsonify({
            "success": True,
            "count": len(result),
            "posts": result
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500