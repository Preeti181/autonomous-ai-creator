import uuid

from flask import Blueprint, jsonify, request

from database.db import db
from models.agent import Agent


agent_bp = Blueprint("agent", __name__)


@agent_bp.route("/api/agent/init", methods=["POST"])
def initialize_agent():
    """Initialize the AI persona once."""

    data = request.get_json(silent=True)

    if not data or not isinstance(data.get("persona"), dict):
        return jsonify({
            "error": "persona is required"
        }), 400

    persona = data["persona"]

    name = persona.get("name")
    domain = persona.get("domain")

    if not isinstance(name, str) or not name.strip():
        return jsonify({
            "error": "persona name is required"
        }), 400

    if not isinstance(domain, str) or not domain.strip():
        return jsonify({
            "error": "persona domain is required"
        }), 400

    existing_agent = Agent.query.first()

    if existing_agent:
        return jsonify({
            "error": "Agent is already initialized",
            "agentId": existing_agent.id
        }), 409

    agent = Agent(
        id=str(uuid.uuid4()),
        name=name.strip(),
        domain=domain.strip(),
        voice="Professional, analytical, simple, educational"
    )

    db.session.add(agent)
    db.session.commit()

    return jsonify({
        "agentId": agent.id
    }), 201