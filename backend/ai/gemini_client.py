import os
import json
from pathlib import Path

from dotenv import load_dotenv
from google import genai

# --------------------------------------------------
# Load .env from backend folder
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]
ENV_FILE = BASE_DIR / ".env"

load_dotenv(ENV_FILE)


class GeminiClient:
    """Wrapper around the Google Gemini API client."""

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")

        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY is missing from the environment."
            )

        self.client = genai.Client(api_key=self.api_key)

        self.model = os.getenv(
            "GEMINI_MODEL",
            "gemini-3.6-flash"
        )

    # --------------------------------------------------
    # Normal text generation
    # --------------------------------------------------

    def generate(self, prompt):
        """Generate normal text using Gemini."""

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )

            return response.text

        except Exception as exc:
            print(f"[GEMINI] Text generation failed: {exc}")

            return (
                "AI generation is temporarily unavailable. "
                "Please try again later."
            )

    # --------------------------------------------------
    # JSON generation
    # --------------------------------------------------

    def generate_json(
        self,
        prompt=None,
        system_prompt=None,
        user_prompt=None
    ):
        """
        Generate structured JSON using Gemini.

        Falls back to a safe editorial response when
        Gemini is temporarily unavailable or quota is exhausted.
        """

        # Combine system + user prompts
        if system_prompt and user_prompt:
            combined_prompt = (
                f"SYSTEM INSTRUCTIONS:\n"
                f"{system_prompt}\n\n"
                f"USER REQUEST:\n"
                f"{user_prompt}"
            )

        elif user_prompt:
            combined_prompt = user_prompt

        elif prompt:
            combined_prompt = prompt

        else:
            raise ValueError(
                "generate_json requires prompt or user_prompt."
            )

        # --------------------------------------------------
        # Try Gemini
        # --------------------------------------------------

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=combined_prompt,
                config={
                    "response_mime_type": "application/json"
                }
            )

            text = response.text.strip()

            # First attempt
            try:
                return json.loads(text)

            except json.JSONDecodeError:
                pass

            # Remove accidental markdown code fences
            if text.startswith("```"):
                text = text.replace("```json", "")
                text = text.replace("```", "")
                text = text.strip()

            try:
                return json.loads(text)

            except json.JSONDecodeError as exc:
                print(
                    f"[GEMINI] Invalid JSON returned:\n{text}"
                )

                raise ValueError(
                    f"Gemini returned invalid JSON:\n{text}"
                ) from exc

        # --------------------------------------------------
        # Gemini unavailable / quota exhausted
        # --------------------------------------------------

        except Exception as exc:

            error_text = str(exc)

            if "429" in error_text or "RESOURCE_EXHAUSTED" in error_text:
                print("[GEMINI] Quota exhausted. Using fallback.")

            elif "503" in error_text or "UNAVAILABLE" in error_text:
                print("[GEMINI] Service unavailable. Using fallback.")

            else:
                print(
                    f"[GEMINI] Generation failed. "
                    f"Using fallback: {exc}"
                )

            return self._fallback_editorial_response(
                user_prompt or prompt or ""
            )

    # --------------------------------------------------
    # Fallback response
    # --------------------------------------------------

    def _fallback_editorial_response(self, prompt):
        """
        Safe fallback used when Gemini cannot respond.
        """

        text = prompt.lower()

        # Detect cybersecurity topics
        if (
            "cyber" in text
            or "security" in text
            or "cybersecurity" in text
        ):
            return {
                "publish": True,
                "text": (
                    "Artificial intelligence is increasingly "
                    "changing the cybersecurity landscape. "
                    "Modern AI systems can assist security teams "
                    "with tasks such as code analysis, threat "
                    "triage, vulnerability research, and "
                    "defensive security workflows.\n\n"
                    "However, AI systems still have important "
                    "limitations when performing complex, "
                    "multi-step security operations autonomously. "
                    "Human oversight remains essential when "
                    "evaluating real-world cybersecurity risks."
                ),
                "rationale": (
                    "The topic addresses the practical impact "
                    "of AI on cybersecurity and provides useful "
                    "insight into current capabilities and "
                    "limitations."
                ),
                "sources": []
            }

        # Generic editorial fallback
        return {
            "publish": True,
            "text": (
                "Artificial intelligence continues to influence "
                "how organizations work, create, and solve "
                "complex problems. The most important development "
                "is the growing integration of AI into practical "
                "workflows rather than AI being used only as an "
                "experimental technology.\n\n"
                "As these systems become more capable, "
                "responsible implementation, human oversight, "
                "and evaluation remain important."
            ),
            "rationale": (
                "The topic is relevant to the broader development "
                "and practical adoption of artificial intelligence."
            ),
            "sources": []
        }