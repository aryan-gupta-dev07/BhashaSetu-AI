from pathlib import Path

from gnani.stt import GnaniSTTClient

from config import GNANI_API_KEY


def _transcribe_audio(audio_path, language_code, language_name):
    """Transcribe an audio file using the Gnani STT API."""

    audio_path = Path(audio_path)

    if not GNANI_API_KEY:
        raise RuntimeError("GNANI_API_KEY is not configured.")

    if not audio_path.is_file():
        raise FileNotFoundError(
            f"Audio file not found: {audio_path}"
        )

    if audio_path.stat().st_size == 0:
        raise ValueError(
            f"Audio file is empty: {audio_path}"
        )

    client = GnaniSTTClient(api_key=GNANI_API_KEY)

    result = client.transcribe_bytes(
        audio_path.read_bytes(),
        filename=audio_path.name,
        language_code=language_code,
    )

    if not result.get("success") or not result.get("transcript"):
        raise RuntimeError(
            f"{language_name} speech recognition failed."
        )

    return result["transcript"]


def transcribe_hindi_audio(audio_path):
    """Transcribe Hindi audio into Hindi text."""

    return _transcribe_audio(
        audio_path=audio_path,
        language_code="hi-IN",
        language_name="Hindi",
    )


def transcribe_gujarati_audio(audio_path):
    """Transcribe Gujarati audio into Gujarati text."""

    return _transcribe_audio(
        audio_path=audio_path,
        language_code="gu-IN",
        language_name="Gujarati",
    )