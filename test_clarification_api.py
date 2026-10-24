from services.clarification import check_instruction_clarity


def main():
    instruction = "Please finish the work as soon as possible."

    print("Testing BhashaSetu AI Ask-Back...")
    print("Instruction:", instruction)

    result = check_instruction_clarity(
        instruction=instruction,
        language="English",
    )

    print("\nAPI response:")
    print("Status:", result["status"])
    print("Reason:", result["reason"])
    print("Question:", result["question"])

    assert result["status"] in {
        "CLEAR",
        "NEEDS_CLARIFICATION",
    }

    assert isinstance(result["reason"], str)

    if result["status"] == "NEEDS_CLARIFICATION":
        assert isinstance(result["question"], str)

    print("\nAPI test passed!")


if __name__ == "__main__":
    main()