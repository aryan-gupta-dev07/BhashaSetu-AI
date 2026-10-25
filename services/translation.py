import requests

from config import GROQ_API_KEY, GROQ_MODEL, GROQ_URL


def _translate_text(text, source_language, target_language):
    """Translate text using the Groq API."""

    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY is not configured.")

    if not isinstance(text, str) or not text.strip():
        raise ValueError("Input text must not be empty.")

    response = requests.post(
        GROQ_URL,
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": GROQ_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        f"Translate the following workplace instruction "
                        f"from {source_language} into natural "
                        f"{target_language}. Preserve the original "
                        f"meaning. Preserve the meaning of all numbers, dates, "
                        f"times, quantities, names, and negative instructions. "
                        f"Never turn a negative instruction into a positive one. "
                        f"Preserve the relationship between dates, deadlines, and times. "
                        f"If the original instruction is ambiguous, do not invent details. "
                        f"Return only the translation."
                    ),
                },
                {
                    "role": "user",
                    "content": text.strip(),
                },
            ],
            "temperature": 0,
        },
        timeout=60,
    )

    response.raise_for_status()

    data = response.json()
    translated_text = (
        data["choices"][0]["message"]["content"].strip()
    )

    if not translated_text:
        raise RuntimeError("Translation API returned empty text.")

    return translated_text


def translate_to_gujarati(hindi_text):
    """Translate Hindi text into Gujarati."""

    return _translate_text(
        text=hindi_text,
        source_language="Hindi",
        target_language="Gujarati",
    )


def translate_to_hindi(gujarati_text):
    """Translate Gujarati text into Hindi."""

    return _translate_text(
        text=gujarati_text,
        source_language="Gujarati",
        target_language="Hindi",
    )