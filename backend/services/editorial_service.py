"""
Editorial Decision Service.

Connects the topic selection system with the AI editorial engine.
"""

from ai.gemini_client import GeminiClient
from ai.prompts import (
    EDITORIAL_SYSTEM_PROMPT,
    build_editorial_prompt,
)
from utils.source_cleaner import clean_sources


class EditorialService:
    """
    Determines whether a selected topic should become a post.
    """

    def __init__(self):
        self.client = GeminiClient()

    def evaluate_topic(self, topic) -> dict:
        """
        Ask the AI to evaluate a topic and generate a post
        when appropriate.
        """

        user_prompt = build_editorial_prompt(topic)

        result = self.client.generate_json(
            system_prompt=EDITORIAL_SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )

        return self._validate_result(result, topic)

    @staticmethod
    def _validate_result(result: dict, topic) -> dict:
        """
        Validate and normalize the AI response.
        """

        publish = bool(result.get("publish", False))
        text = result.get("text", "")
        rationale = result.get("rationale", "")
        sources = result.get("sources", [])

        if not isinstance(sources, list):
            sources = []

        # Always preserve the original topic source.
        original_url = getattr(topic, "url", "")

        if original_url:
            sources.append(original_url)

        # Clean Markdown URLs and remove duplicates.
        sources = clean_sources(sources)

        if publish and not text:
            publish = False
            rationale = (
                "Rejected because the AI did not generate "
                "a valid publication."
            )

        return {
            "publish": publish,
            "text": str(text).strip(),
            "rationale": str(rationale).strip(),
            "sources": sources,
        }


def evaluate_topic(topic) -> dict:
    """
    Convenience function for the rest of the application.
    """

    service = EditorialService()
    return service.evaluate_topic(topic)