from flask import Blueprint, request, jsonify
from datetime import datetime

from database.db import db
from models.topic import Topic
from models.post import Post

agent_bp = Blueprint("agent", __name__, url_prefix="/api/agent")


@agent_bp.route("/init", methods=["POST"])
def init_agent():
    data = request.get_json(silent=True) or {}

    persona = data.get("persona")

    if not persona:
        return jsonify({"error": "persona is required"}), 400

    return jsonify({
        "success": True,
        "message": "Agent initialized successfully",
        "persona": persona
    })


@agent_bp.route("/feed", methods=["GET"])
def feed():

    topics = Topic.query.order_by(Topic.id.desc()).limit(10).all()
    posts = Post.query.order_by(Post.id.desc()).limit(10).all()

    return jsonify({
        "success": True,
        "topics": [
            {
                "id": t.id,
                "title": t.title,
                "status": t.status
            }
            for t in topics
        ],
        "posts": [
            {
                "id": p.id,
                "topic_id": p.topic_id,
                "content": p.content,
                "rationale": p.rationale,
                "status": p.status,
                "sources": p.sources,
                "created_at": str(p.created_at),
                "published_at": str(p.published_at)
                if p.published_at else None
            }
            for p in posts
        ]
    })


@agent_bp.route("/posts", methods=["GET"])
def get_posts():

    posts = Post.query.order_by(Post.id.desc()).all()

    return jsonify({
        "success": True,
        "posts": [
            {
                "id": p.id,
                "topic_id": p.topic_id,
                "content": p.content,
                "rationale": p.rationale,
                "sources": p.sources,
                "status": p.status,
                "created_at": str(p.created_at),
                "published_at": str(p.published_at)
                if p.published_at else None
            }
            for p in posts
        ]
    })


@agent_bp.route("/posts/<int:post_id>/publish", methods=["POST"])
def publish_post(post_id):

    post = Post.query.get(post_id)

    if not post:
        return jsonify({
            "success": False,
            "error": "Post not found"
        }), 404

    post.status = "published"
    post.published_at = datetime.utcnow()

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Post published successfully",
        "post_id": post.id,
        "status": post.status,
        "published_at": str(post.published_at)
    })


@agent_bp.route("/topics", methods=["GET"])
def get_topics():

    topics = Topic.query.order_by(Topic.id.desc()).all()

    return jsonify({
        "success": True,
        "topics": [
            {
                "id": t.id,
                "title": t.title,
                "status": t.status
            }
            for t in topics
        ]
    })