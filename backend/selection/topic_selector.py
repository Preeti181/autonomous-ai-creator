"""
Autonomous Topic Selection Engine

Evaluates discovered topics and decides which topics are worth
sending to the editorial AI for possible publication.
"""

from datetime import datetime, timezone
from typing import Iterable, List, Optional


# Strong AI and technology signals.
POSITIVE_KEYWORDS = {
    "ai": 12,
    "artificial intelligence": 15,
    "machine learning": 12,
    "deep learning": 10,
    "generative ai": 15,
    "llm": 15,
    "large language model": 15,
    "gpt": 15,
    "gemini": 15,
    "chatgpt": 12,
    "claude": 12,
    "deepseek": 12,
    "ai agent": 15,
    "agentic": 15,
    "robotics": 15,
    "robot": 10,
    "computer vision": 12,
    "natural language": 10,
    "cybersecurity": 15,
    "cyber security": 15,
    "cyber": 8,
    "security": 8,
    "open source": 12,
    "developer": 8,
    "software": 8,
    "coding": 10,
    "programming": 8,
    "python": 8,
    "gpu": 10,
    "chip": 8,
    "semiconductor": 10,
    "cloud": 7,
    "technology": 6,
    "tech": 6,
    "data": 6,
    "model": 6,
}


# Topics that should normally be rejected.
NEGATIVE_KEYWORDS = {
    "celebrity",
    "gossip",
    "sports",
    "cricket",
    "football",
    "movie review",
    "entertainment gossip",
    "fashion",
    "recipe",
    "cooking",
}


def get_topic_text(topic) -> str:
    """Return searchable text from a topic."""

    title = getattr(topic, "title", "") or ""
    description = getattr(topic, "description", "") or ""

    return f"{title} {description}".strip()


def calculate_topic_score(topic) -> float:
    """
    Calculate an editorial relevance score from 0 to 100.

    The score represents how strongly the topic matches the
    AI and technology persona.
    """

    text = get_topic_text(topic).lower()

    if not text:
        return 0.0

    score = 0.0

    # Positive AI/technology signals.
    for keyword, points in POSITIVE_KEYWORDS.items():
        if keyword in text:
            score += points

    # Negative signals.
    for keyword in NEGATIVE_KEYWORDS:
        if keyword in text:
            score -= 30

    # Reward informative titles.
    if len(text) >= 50:
        score += 5

    # Stronger reward when multiple AI/technology concepts appear.
    matched_keywords = [
        keyword
        for keyword in POSITIVE_KEYWORDS
        if keyword in text
    ]

    if len(matched_keywords) >= 2:
        score += 10

    if len(matched_keywords) >= 3:
        score += 10

    return round(max(0.0, min(100.0, score)), 1)


def is_publishable(
    topic,
    minimum_score: float = 20.0,
) -> bool:
    """Return True when a topic passes the editorial threshold."""

    return calculate_topic_score(topic) >= minimum_score


def select_topics(
    topics: Iterable,
    minimum_score: float = 20.0,
    limit: Optional[int] = 5,
) -> List:
    """
    Evaluate all topics and return the strongest candidates.

    Topics below the editorial threshold are intentionally rejected.
    """

    candidates = []

    for topic in topics:

        score = calculate_topic_score(topic)

        # Keep the score available to later services.
        try:
            topic.selection_score = score
        except Exception:
            pass

        if score >= minimum_score:
            candidates.append(topic)

    # Highest-quality topics first.
    candidates.sort(
        key=lambda topic: getattr(
            topic,
            "selection_score",
            0
        ),
        reverse=True,
    )

    if limit is not None:
        candidates = candidates[:limit]

    return candidates


def select_best_topic(
    topics: Iterable,
    minimum_score: float = 20.0,
):
    """Return the strongest topic or None."""

    selected = select_topics(
        topics,
        minimum_score=minimum_score,
        limit=1,
    )

    if not selected:
        return None

    return selected[0]


def build_selection_rationale(topic) -> str:
    """
    Explain why the topic was selected.

    This will later be returned through the feed API.
    """

    score = calculate_topic_score(topic)

    title = getattr(
        topic,
        "title",
        "Unknown topic"
    )

    source = getattr(
        topic,
        "source",
        "Unknown source"
    )

    return (
        f"The topic '{title}' was selected because it scored "
        f"{score}/100 for relevance to the AI and technology "
        f"persona. It was discovered from {source} and passed "
        f"the editorial relevance threshold. Topics are prioritized "
        f"when they provide meaningful developments, technical "
        f"insights, or important implications for the AI ecosystem."
    )


def build_rejection_reason(topic) -> str:
    """
    Explain why a topic was rejected.
    """

    score = calculate_topic_score(topic)

    title = getattr(
        topic,
        "title",
        "Unknown topic"
    )

    return (
        f"The topic '{title}' was rejected because it scored "
        f"{score}/100, which is below the editorial threshold. "
        f"The autonomous agent intentionally rejects topics that "
        f"are not sufficiently relevant to its AI and technology "
        f"persona."
    )


def selection_summary(
    topics: Iterable,
    minimum_score: float = 20.0,
) -> dict:
    """
    Return selection statistics for debugging and dashboard use.
    """

    topics = list(topics)

    selected = select_topics(
        topics,
        minimum_score=minimum_score,
        limit=None,
    )

    return {
        "evaluated": len(topics),
        "selected": len(selected),
        "rejected": len(topics) - len(selected),
        "minimum_score": minimum_score,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }