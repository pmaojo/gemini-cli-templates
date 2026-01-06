"""
Translation Service
Provides efficient translation to English using lightweight LLMs.
Ensures all input data is in English before reaching the SLM.
"""
import os
import json
from typing import Dict, Any, Union
from litellm import completion

class TranslationService:
    def __init__(self, model: str = "gemini-3-flash"):
        # Allow override via env var, but default to the efficient Flash model
        self.model = os.getenv("TRANSLATION_MODEL", model)
        print(f"🌍 Translation Service initialized with model: {self.model}")

    def translate(self, text: str) -> str:
        """Translate text to English"""
        if not text or not text.strip():
            return text

        try:
            prompt = f"Translate the following text to English. Return ONLY the translation, no explanations.\n\nText: {text}"

            response = completion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0
            )

            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"⚠️ Translation failed: {e}")
            return text # Fallback to original

    def translate_json(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Translate values of a JSON/Dict to English.
        Keeps keys unchanged.
        """
        try:
            # Prepare simple representation for translation
            row_str = json.dumps(data, ensure_ascii=False)

            prompt = f"""Translate the values of this JSON object to English. Keep keys unchanged.
Input: {row_str}
Output JSON:"""

            response = completion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0
            )

            content = response.choices[0].message.content
            if "```" in content:
                content = content.split("```")[1].replace("json", "").strip()

            return json.loads(content)
        except Exception as e:
            print(f"⚠️ JSON Translation failed: {e}")
            return data  # Fallback to original
