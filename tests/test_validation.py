from pathlib import Path
from unittest.mock import patch

import pytest

from app import smart_workplace_translation
from services.speech_to_text import transcribe_hindi_audio
from services.translation import translate_to_gujarati
from services.text_to_speech import generate_hindi_audio


def test_missing_audio_file():
    with pytest.raises(FileNotFoundError):
        transcribe_hindi_audio(Path("missing_test_audio.wav"))


def test_empty_translation_input():
    with pytest.raises(ValueError):
        translate_to_gujarati("")


def test_empty_tts_input():
    with pytest.raises(ValueError):
        generate_hindi_audio("", Path("empty_test_audio.wav"))


def test_smart_translation_rejects_empty_instruction(capsys):
    with patch("builtins.input", side_effect=[""]):
        smart_workplace_translation()

    captured = capsys.readouterr()

    assert "Please enter an instruction." in captured.out
    assert "Translated instruction:" not in captured.out
    assert "Audio generated at:" not in captured.out


def test_smart_translation_rejects_same_source_and_target_language(capsys):
    with patch(
        "builtins.input",
        side_effect=[
            "आज मीटिंग सुबह 10 बजे शुरू होगी।",
            "hindi",
            "hindi",
            "exit",
        ],
    ):
        smart_workplace_translation()

    captured = capsys.readouterr()

    assert "Source and target languages must be different." in captured.out
    assert "Translated instruction:" not in captured.out
    assert "Audio generated at:" not in captured.out


def test_smart_translation_stops_when_instruction_is_unclear(capsys):
    unclear_result = {
        "status": "NEEDS_CLARIFICATION",
        "reason": "The instruction is ambiguous.",
        "question": "Which task should be done soon?",
    }

    with (
        patch(
            "builtins.input",
            side_effect=["Do it soon.", "hindi", "gujarati", "exit"],
        ),
        patch("app.check_instruction_clarity", return_value=unclear_result),
    ):
        smart_workplace_translation()

    captured = capsys.readouterr()

    assert "Follow-up question:" in captured.out
    assert "Translated instruction:" not in captured.out
    assert "Audio generated at:" not in captured.out


def test_smart_translation_rejects_unsupported_source_language(capsys):
    with patch(
        "builtins.input",
        side_effect=[
            "Hello, start the meeting.",
            "english",
            "gujarati",
            "exit",
        ],
    ):
        smart_workplace_translation()

    captured = capsys.readouterr()

    assert "Unsupported source language." in captured.out
    assert "Translated instruction:" not in captured.out
    assert "Audio generated at:" not in captured.out

from unittest.mock import Mock

from services.translation import translate_to_gujarati


def test_translation_prompt_preserves_numbers(monkeypatch):
    import services.translation as translation

    monkeypatch.setattr(translation, "GROQ_API_KEY", "test-key")

    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = {
        "choices": [{"message": {"content": "મીટિંગમાં 25 લોકો આવશે."}}]
    }

    def fake_post(*args, **kwargs):
        prompt = kwargs["json"]["messages"][0]["content"]
        assert "Preserve the original meaning." in prompt
        assert "25" in kwargs["json"]["messages"][1]["content"]
        return response

    monkeypatch.setattr(translation.requests, "post", fake_post)

    result = translate_to_gujarati("મીટિંગમાં 25 લોકો આવશે.")
    assert "25" in result


def test_translation_prompt_preserves_dates(monkeypatch):
    import services.translation as translation

    monkeypatch.setattr(translation, "GROQ_API_KEY", "test-key")

    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = {
        "choices": [{"message": {"content": "મીટિંગ 25 ડિસેમ્બરે છે."}}]
    }

    def fake_post(*args, **kwargs):
        assert "25 December" in kwargs["json"]["messages"][1]["content"]
        return response

    monkeypatch.setattr(translation.requests, "post", fake_post)

    result = translate_to_gujarati("Meeting is on 25 December.")
    assert "25" in result


def test_translation_prompt_preserves_negation(monkeypatch):
    import services.translation as translation

    monkeypatch.setattr(translation, "GROQ_API_KEY", "test-key")

    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = {
        "choices": [{"message": {"content": "આજે કામ કરશો નહીં."}}]
    }

    def fake_post(*args, **kwargs):
        assert "Do not" in kwargs["json"]["messages"][1]["content"]
        return response

    monkeypatch.setattr(translation.requests, "post", fake_post)

    result = translate_to_gujarati("Do not work today.")
    assert "નહીં" in result

def test_smart_translation_rejects_unsupported_target_language(capsys):
    with patch(
        "builtins.input",
        side_effect=[
            "Hello, start the meeting.",
            "hindi",
            "english",
            "exit",
        ],
    ):
        smart_workplace_translation()

    captured = capsys.readouterr()

    assert "Unsupported target language." in captured.out
    assert "Translated instruction:" not in captured.out
    assert "Audio generated at:" not in captured.out
