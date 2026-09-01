"""Prompt Manager — central access point for localized prompt templates."""

from first_aid_rag.prompts.templates.locales import ar, en

_LOCALES = {"en": en, "ar": ar}


def detect_locale(text: str) -> str:
    """Return 'ar' when the text contains Arabic characters, else 'en'."""
    return "ar" if any("\u0600" <= ch <= "\u06FF" for ch in text) else "en"


class PromptManager:
    """Formats and serves language-specific prompts for the RAG pipeline."""

    def get_system_prompt(self, locale: str = "en") -> str:
        """The system prompt is locale-agnostic (it embeds language-matching rules)."""
        return _LOCALES.get(locale, en).SYSTEM_PROMPT

    def get_insufficient_evidence_refusal(self, locale: str = "en") -> str:
        return _LOCALES.get(locale, en).REFUSAL_INSUFFICIENT_EVIDENCE

    def get_out_of_scope_refusal(self, locale: str = "en") -> str:
        return _LOCALES.get(locale, en).REFUSAL_OUT_OF_SCOPE
