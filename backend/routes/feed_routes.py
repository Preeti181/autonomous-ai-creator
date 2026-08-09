from flask import Blueprint, jsonify

feed_bp = Blueprint("feed", __name__, url_prefix="/api/feed")


@feed_bp.route("", methods=["GET"])
@feed_bp.route("/", methods=["GET"])
def get_feed():
    """
    Return the AI creator feed.

    This is intentionally safe and database-independent for now.
    It allows the deployed dashboard to communicate with the backend
    without disturbing the existing database/models.
    """

    return jsonify({
        "success": True,
        "posts": [],
        "total": 0,
        "message": "AI feed is ready. No posts have been generated yet."
    }), 200


@feed_bp.route("/health", methods=["GET"])
def feed_health():
    return jsonify({
        "success": True,
        "service": "feed",
        "status": "online"
    }), 200