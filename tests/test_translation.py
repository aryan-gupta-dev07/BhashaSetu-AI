from unittest.mock import Mock, patch

import pytest

from services.translation import (
    _translate_text,
    translate_to_gujarati,
    translate_to_hindi,
)


@patch("services.translation.requests.post")
def test_translate_to_gujarati_preserves_critical_details(mock_post):
    mock_response = Mock()
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": "મશીન 4 સવારે 10 વાગ્યે બંધ કરો."
                }
            }
        ]
    }
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    result = translate_to_gujarati(
        "Machine 4 ko subah 10 baje band karo."
    )

    assert result == "મશીન 4 સવારે 10 વાગ્યે બંધ કરો."

    request_data = mock_post.call_args.kwargs["json"]

    assert request_data["temperature"] == 0
    assert request_data["messages"][0]["role"] == "system"

    prompt = request_data["messages"][0]["content"].lower()

    assert "numbers" in prompt
    assert "times" in prompt
    assert "negative instructions" in prompt


@patch("services.translation.requests.post")
def test_translate_to_hindi(mock_post):
    mock_response = Mock()
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": "मशीन 4 सुबह 10 बजे बंद करो।"
                }
            }
        ]
    }
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    result = translate_to_hindi(
        "મશીન 4 સવારે 10 વાગ્યે બંધ કરો."
    )

    assert result == "मशीन 4 सुबह 10 बजे बंद करो।"

    request_data = mock_post.call_args.kwargs["json"]
    assert request_data["temperature"] == 0


def test_translation_rejects_empty_input():
    with pytest.raises(ValueError, match="must not be empty"):
        _translate_text("", "Hindi", "Gujarati")


def test_translation_rejects_whitespace_input():
    with pytest.raises(ValueError, match="must not be empty"):
        _translate_text("   ", "Hindi", "Gujarati")


@patch("services.translation.GROQ_API_KEY", "")
def test_translation_rejects_missing_api_key():
    with pytest.raises(RuntimeError, match="not configured"):
        _translate_text("Namaste", "Hindi", "Gujarati")


@patch("services.translation.requests.post")
def test_translation_rejects_empty_api_response(mock_post):
    mock_response = Mock()
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": "   "
                }
            }
        ]
    }
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    with pytest.raises(RuntimeError, match="empty text"):
        _translate_text("Namaste", "Hindi", "Gujarati")