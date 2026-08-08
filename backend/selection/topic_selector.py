"""
Topic Selection Engine

Responsible for deciding which discovered AI/technology topics
are worth considering for publication.
"""

from datetime import datetime, timezone
from typing import Iterable, List, Optional

try:
    from models.topic import Topic
except ImportError:
    Topic = None


# Topics that are highly relevant to our AI/technology persona.
POSITIVE_KEYWORDS = {
    "artificial intelligence",
    "ai",
    "machine learning",
    "deep learning",
    "generative ai",
    "llm",
    "large language model",
    "agentic ai",
    "ai agent",
    "robotics",
    "computer vision",
    "natural language processing",
    "open source",
    "cybersecurity",
    "ai security",
    "developer",
    "software engineering",
    "python",
    "technology",
    "cloud",
    "gpu",
    "semiconductor",
}

# Topics that should normally be rejected.
NEGATIVE_KEYWORDS = {
    "celebrity",
    "sports",
    "cricket",
    "football",
    "movie",
    "entertainment",
    "gossip",
    "politics",
    "weather",
    "recipe",
    "fashion",
}

# Topics that are too generic to be useful.
GENERIC_WORDS = {
    "news",
    "update",
    "latest",
    "story",
}


def _get_text(topic) -> str:
    """
    Safely combine the title and description of a topic.
    """
    title = getattr(topic, "title", "") or ""
    description = getattr(topic, "description", "") or ""

    return f"{title} {description}".strip()


def calculate_topic_score(topic) -> float:
    """
    Calculate a simple editorial relevance score from 0 to 100.

    Higher score = stronger candidate for publication.
    """

    text = _get_text(topic).lower()

    if not text:
        return 0.0

    score = 0.0

    # Strong relevance signals.
    for keyword in POSITIVE_KEYWORDS:
        if keyword in text:
            score += 8

    # Strong rejection signals.
    for keyword in NEGATIVE_KEYWORDS:
        if keyword in text:
            score -= 25

    # Penalize extremely short topics.
    if len(text) < 30:
        score -= 10

    # Reward useful longer descriptions.
    if len(text) >= 100:
        score += 5

    # Avoid completely generic headlines.
    words = set(text.split())
    generic_matches = len(words.intersection(GENERIC_WORDS))

    score -= generic_matches * 2

    return max(0.0, min(100.0, score))


def is_publishable(
    topic,
    minimum_score: float = 25.0,
) -> bool:
    """
    Decide whether a topic passes the editorial threshold.
    """

    score = calculate_topic_score(topic)

    return score >= minimum_score


def select_topics(
    topics: Iterable,
    minimum_score: float = 25.0,
    limit: Optional[int] = 5,
) -> List:
    """
    Select the strongest topics from a collection.

    Topics are scored, rejected topics are removed,
    and the remaining topics are sorted from highest
    score to lowest score.
    """

    candidates = []

    for topic in topics:
        score = calculate_topic_score(topic)

        # Store the score on the object when possible.
        try:
            topic.selection_score = score
        except Exception:
            pass

        if score >= minimum_score:
            candidates.append(topic)

    candidates.sort(
        key=lambda item: getattr(item, "selection_score", 0),
        reverse=True,
    )

    if limit is not None:
        candidates = candidates[:limit]

    return candidates


def build_selection_rationale(topic) -> str:
    """
    Explain why the topic was selected.

    This rationale can later be returned through the feed API.
    """

    score = calculate_topic_score(topic)

    title = getattr(topic, "title", "Unknown topic")
    source = getattr(topic, "source", "Unknown source")

    return (
        f"Selected '{title}' because it scored {score:.1f}/100 "
        f"on AI/technology relevance. The topic was discovered from "
        f"{source} and passed the minimum editorial relevance threshold. "
        f"The selection favors topics that provide useful, timely "
        f"information for an AI and technology-focused audience."
    )


def build_rejection_reason(topic) -> str:
    """
    Explain why a topic was rejected.
    """

    score = calculate_topic_score(topic)

    title = getattr(topic, "title", "Unknown topic")

    return (
        f"Rejected '{title}' because its editorial relevance score "
        f"was {score:.1f}/100, below the required threshold. "
        f"The agent intentionally filters topics that are not sufficiently "
        f"relevant to its AI and technology persona."
    )


def select_best_topic(
    topics: Iterable,
    minimum_score: float = 25.0,
):
    """
    Return the single strongest topic.

    Returns None when no topic passes the editorial threshold.
    """

    selected = select_topics(
        topics,
        minimum_score=minimum_score,
        limit=1,
    )

    if not selected:
        return None

    return selected[0]


def selection_summary(
    topics: Iterable,
    minimum_score: float = 25.0,
) -> dict:
    """
    Return a simple summary useful for debugging and the dashboard.
    """

    topics = list(topics)

    selected = select_topics(
        topics,
        minimum_score=minimum_score,
        limit=None,
    )

    rejected_count = len(topics) - len(selected)

    return {
        "evaluated": len(topics),
        "selected": len(selected),
        "rejected": rejected_count,
        "minimum_score": minimum_score,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }