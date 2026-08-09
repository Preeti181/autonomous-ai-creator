import logging
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import feedparser

from database.db import db
from models.topic import Topic


logger = logging.getLogger(__name__)


RSS_FEEDS = {
    "OpenAI": "https://openai.com/news/rss.xml",
    "Google DeepMind": "https://deepmind.google/blog/rss.xml",
    "Hacker News": "https://hnrss.org/frontpage",
}


def parse_date(entry):
    """Return a timezone-aware datetime for an RSS entry."""

    published = entry.get("published") or entry.get("updated")

    if not published:
        return datetime.now(timezone.utc)

    try:
        return parsedate_to_datetime(published).astimezone(timezone.utc)
    except (TypeError, ValueError, OverflowError):
        return datetime.now(timezone.utc)


def collect_topics():
    """Collect new topics from configured RSS feeds."""

    discovered_topics = []

    for source, feed_url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(feed_url)

            if feed.bozo and not feed.entries:
                logger.warning("Failed to read RSS feed: %s", source)
                continue

            for entry in feed.entries[:10]:
                title = entry.get("title", "").strip()
                url = entry.get("link", "").strip()

                if not title or not url:
                    continue

                existing_topic = Topic.query.filter_by(url=url).first()

                if existing_topic:
                    continue

                topic = Topic(
                    title=title,
                    source=source,
                    url=url,
                    score=0.0,
                    status="discovered",
                    reason=None,
                    created_at=parse_date(entry),
                )

                db.session.add(topic)
                discovered_topics.append(topic)

            db.session.commit()

        except Exception as exc:
            db.session.rollback()
            logger.exception(
                "Error collecting topics from %s: %s",
                source,
                exc,
            )

    return discovered_topics