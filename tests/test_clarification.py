import pytest

from services.clarification import check_instruction_clarity


def test_empty_instruction():
    with pytest.raises(ValueError, match="Instruction cannot be empty."):
        check_instruction_clarity("")


def test_whitespace_instruction():
    with pytest.raises(ValueError, match="Instruction cannot be empty."):
        check_instruction_clarity("   ")


def test_missing_language():
    with pytest.raises(ValueError, match="Language cannot be empty."):
        check_instruction_clarity(
            "Please finish the work.",
            language="   ",
        )


def test_clear_instruction_response(monkeypatch):
    def fake_post(*args, **kwargs):
        class FakeResponse:
            def raise_for_status(self):
                pass

            def json(self):
                return {
                    "choices": [
                        {
                            "message": {
                                "content": (
                                    '{"status": "CLEAR", '
                                    '"reason": "The instruction is clear.", '
                                    '"question": null}'
                                )
                            }
                        }
                    ]
                }

        return FakeResponse()

    monkeypatch.setattr(
        "services.clarification.requests.post",
        fake_post,
    )

    result = check_instruction_clarity(
        "Please close the door.",
        language="English",
    )

    assert result["status"] == "CLEAR"
    assert result["reason"] == "The instruction is clear."
    assert result["question"] is None


def test_ambiguous_instruction_response(monkeypatch):
    def fake_post(*args, **kwargs):
        class FakeResponse:
            def raise_for_status(self):
                pass

            def json(self):
                return {
                    "choices": [
                        {
                            "message": {
                                "content": (
                                    '{"status": "NEEDS_CLARIFICATION", '
                                    '"reason": "The deadline is missing.", '
                                    '"question": "By what time must the work be completed?"}'
                                )
                            }
                        }
                    ]
                }

        return FakeResponse()

    monkeypatch.setattr(
        "services.clarification.requests.post",
        fake_post,
    )

    result = check_instruction_clarity(
        "Please finish the work soon.",
        language="English",
    )

    assert result["status"] == "NEEDS_CLARIFICATION"
    assert result["reason"] == "The deadline is missing."
    assert isinstance(result["question"], str)
    assert result["question"]


def test_invalid_api_status(monkeypatch):
    def fake_post(*args, **kwargs):
        class FakeResponse:
            def raise_for_status(self):
                pass

            def json(self):
                return {
                    "choices": [
                        {
                            "message": {
                                "content": (
                                    '{"status": "UNKNOWN", '
                                    '"reason": "Test", '
                                    '"question": null}'
                                )
                            }
                        }
                    ]
                }

        return FakeResponse()

    monkeypatch.setattr(
        "services.clarification.requests.post",
        fake_post,
    )

    with pytest.raises(RuntimeError, match="Invalid clarification status."):
        check_instruction_clarity(
            "Please finish the work.",
            language="English",
            conversation_context="The project deadline is approaching."
        )
        
def test_blank_reason_in_response(monkeypatch):
    import pytest
    from services.clarification import check_instruction_clarity

    class MockResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "choices": [
                    {
                        "message": {
                            "content": (
                                '{"status": "CLEAR", '
                                '"reason": "   ", '
                                '"question": null}'
                            )
                        }
                    }
                ]
            }

    monkeypatch.setattr(
        "services.clarification.requests.post",
        lambda *args, **kwargs: MockResponse(),
    )

    with pytest.raises(RuntimeError, match="Invalid reason"):
        check_instruction_clarity(
            "Submit the report by 5 PM.",
            "English",
        )   
        
def test_missing_clarification_question(monkeypatch):
    import pytest
    from services.clarification import check_instruction_clarity

    class MockResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "choices": [
                    {
                        "message": {
                            "content": (
                                '{"status": "NEEDS_CLARIFICATION", '
                                '"reason": "Deadline is missing", '
                                '"question": null}'
                            )
                        }
                    }
                ]
            }

    monkeypatch.setattr(
        "services.clarification.requests.post",
        lambda *args, **kwargs: MockResponse(),
    )

    with pytest.raises(
        RuntimeError,
        match="Clarification question is missing",
    ):
        check_instruction_clarity(
            "Finish the report soon.",
            "English",
        )   
        
def test_network_failure_is_handled():
    from unittest.mock import patch
    import requests
    import pytest

    with patch(
        "services.clarification.requests.post",
        side_effect=requests.ConnectionError("Network unavailable"),
    ):
        with pytest.raises(RuntimeError, match="API request failed:"):
            check_instruction_clarity("Start the meeting at 10 AM.")    
            
def test_invalid_api_response_is_handled():
    from unittest.mock import patch
    import pytest

    mock_response = patch(
        "services.clarification.requests.post"
    )

    with mock_response as mocked_post:
        mocked_post.return_value.raise_for_status.return_value = None
        mocked_post.return_value.json.return_value = {
            "choices": []
        }

        with pytest.raises(RuntimeError, match="Invalid API response."):
            check_instruction_clarity("Start the meeting at 10 AM.")   
            
def test_context_is_included_in_clarification_prompt():
    from unittest.mock import Mock, patch
    from services.clarification import check_instruction_clarity

    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": (
                        '{"status": "NEEDS_CLARIFICATION", '
                        '"reason": "The timing is unclear.", '
                        '"question": "What time do you mean?"}'
                    )
                }
            }
        ]
    }

    with patch(
        "services.clarification.requests.post",
        return_value=mock_response,
    ) as mock_post:
        check_instruction_clarity(
            instruction="Do it 10 minutes later.",
            language="Hindi",
            conversation_context="Previous instruction: Stop the machine at 5 PM.",
        )

    prompt = mock_post.call_args.kwargs["json"]["messages"][0]["content"]

    assert "Stop the machine at 5 PM." in prompt
    assert "Do it 10 minutes later." in prompt                                   