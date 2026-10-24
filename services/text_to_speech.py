from pathlib import Path

from gnani.tts import GnaniTTSClient

from config import GNANI_API_KEY


def _generate_audio(text, output_path, language, voice):
    """Generate speech audio using the Gnani TTS API."""

    if not GNANI_API_KEY:
        raise RuntimeError("GNANI_API_KEY is not configured.")

    if not isinstance(text, str) or not text.strip():
        raise ValueError("Input text must not be empty.")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    client = GnaniTTSClient(api_key=GNANI_API_KEY)

    client.synthesize(
        text=text.strip(),
        voice=voice,
        model="timbre-v2.5",
        language=language,
        output_file=str(output_path),
    )

    if not output_path.is_file() or output_path.stat().st_size == 0:
        raise RuntimeError(
            "TTS failed to generate a valid audio file."
        )

    return output_path


def generate_gujarati_audio(text, output_path):
    """Generate Gujarati speech audio."""

    return _generate_audio(
        text=text,
        output_path=output_path,
        language="gu-IN",
        voice="Vikrant",
    )


def generate_hindi_audio(text, output_path):
    """Generate Hindi speech audio."""

    return _generate_audio(
        text=text,
        output_path=output_path,
        language="hi-IN",
        voice="Nalini",
    )