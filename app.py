import requests

# Current session's conversation history
CONVERSATION_HISTORY = []
MAX_HISTORY_ITEMS = 5  # Limit the number of previous instructions to consider

from config import BASE_DIR, validate_config

from services.speech_to_text import (
    transcribe_hindi_audio,
    transcribe_gujarati_audio,
)

from services.clarification import check_instruction_clarity


from services.translation import (
    translate_to_gujarati,
    translate_to_hindi,
)

from services.text_to_speech import (
    generate_gujarati_audio,
    generate_hindi_audio,
)


# Project audio files
HINDI_AUDIO_INPUT = BASE_DIR / "Recording.m4a"
GUJARATI_AUDIO_INPUT = BASE_DIR / "gujarati_output.wav"

# Keep input and output files separate.
GUJARATI_AUDIO_OUTPUT = BASE_DIR / "gujarati_translated_output.wav"
HINDI_AUDIO_OUTPUT = BASE_DIR / "hindi_output.wav"


def hindi_to_gujarati():
    """Run the Hindi-to-Gujarati voice translation pipeline."""

    print("\n=== Hindi to Gujarati ===")

    print("\nStep 1: Transcribing Hindi audio...")
    hindi_text = transcribe_hindi_audio(HINDI_AUDIO_INPUT)
    print("Hindi transcript:", hindi_text)

    print("\nStep 2: Translating Hindi text into Gujarati...")
    gujarati_text = translate_to_gujarati(hindi_text)
    print("Gujarati translation:", gujarati_text)

    print("\nStep 3: Generating Gujarati audio...")
    output_path = generate_gujarati_audio(
        gujarati_text,
        GUJARATI_AUDIO_OUTPUT,
    )

    print("Gujarati audio saved:", output_path.resolve())
    print("File size:", output_path.stat().st_size, "bytes")


def gujarati_to_hindi():
    """Run the Gujarati-to-Hindi voice translation pipeline."""

    print("\n=== Gujarati to Hindi ===")

    print("\nStep 1: Transcribing Gujarati audio...")
    gujarati_text = transcribe_gujarati_audio(
        GUJARATI_AUDIO_INPUT
    )
    print("Gujarati transcript:", gujarati_text)

    print("\nStep 2: Translating Gujarati text into Hindi...")
    hindi_text = translate_to_hindi(gujarati_text)
    print("Hindi translation:", hindi_text)

    print("\nStep 3: Generating Hindi audio...")
    output_path = generate_hindi_audio(
        hindi_text,
        HINDI_AUDIO_OUTPUT,
    )

    print("Hindi audio saved:", output_path.resolve())
    print("File size:", output_path.stat().st_size, "bytes")
    
def ask_back():
    """Check whether a workplace instruction needs clarification."""

    print("\n=== BhashaSetu AI: Ask-Back ===")

    instruction = input("\nEnter workplace instruction: ").strip()

    if not instruction:
        print("Please enter an instruction.")
        return

    language = input(
        "Instruction language (Hindi/Gujarati/English): "
    ).strip()

    if not language:
        print("Please enter a language.")
        return

    try:
        result = check_instruction_clarity(
            instruction=instruction,
            language=language,
        )

        print("\n=== Ask-Back Result ===")
        print("Status:", result["status"])
        print("Reason:", result["reason"])

        if result["status"] == "NEEDS_CLARIFICATION":
            print("Follow-up question:", result["question"])
        else:
            print("No clarification needed.")

    except (requests.RequestException, ValueError, RuntimeError) as error:
        print("Ask-Back failed:", error)
        
def smart_workplace_translation():
    """Check clarity, translate instructions, and generate audio."""

    print("\n=== Smart Workplace Translation ===")

    supported_languages = {"hindi", "gujarati"}

    while True:
        instruction = input(
            "\nEnter workplace instruction (or 'exit' to stop): "
        ).strip()

        if instruction.lower() == "exit":
            print("Workflow ended.")
            break

        if not instruction:
            print("Please enter an instruction.")
            break

        recent_history = CONVERSATION_HISTORY[-MAX_HISTORY_ITEMS:]
        conversation_context = "\n".join(recent_history)

        source_language = input(
            "Source language (Hindi/Gujarati): "
        ).strip().lower()

        target_language = input(
            "Target language (Hindi/Gujarati): "
        ).strip().lower()

        if source_language not in supported_languages:
            print("Unsupported source language.")
            continue

        if target_language not in supported_languages:
            print("Unsupported target language.")
            continue

        if source_language == target_language:
            print("Source and target languages must be different.")
            continue

        try:
            result = check_instruction_clarity(
                instruction=instruction,
                language=source_language.title(),
                conversation_context=conversation_context or None,
            )

            print("\n=== Clarity Result ===")
            print("Status:", result["status"])
            print("Reason:", result["reason"])

            if result["status"] == "NEEDS_CLARIFICATION":
                print("Follow-up question:", result["question"])
                print("Translation stopped until clarification is provided.")
                continue

            if result["status"] == "CLEAR":
                if source_language == "hindi":
                    translated_text = translate_to_gujarati(instruction)
                    output_path = GUJARATI_AUDIO_OUTPUT
                    audio_function = generate_gujarati_audio
                else:
                    translated_text = translate_to_hindi(instruction)
                    output_path = HINDI_AUDIO_OUTPUT
                    audio_function = generate_hindi_audio

                print("\nTranslated instruction:", translated_text)

                audio_function(translated_text, output_path)
                print("Audio generated at:", output_path)

                CONVERSATION_HISTORY.append(
                    f"Previous workplace instruction: {instruction}"
                )
                del CONVERSATION_HISTORY[:-MAX_HISTORY_ITEMS]

        except (
            requests.RequestException,
            ValueError,
            RuntimeError,
        ) as error:
            print("Workflow failed:", error)
            
            
def main():
    """Display the menu and run the selected workflow."""

    print("\n=== BhashaSetu AI ===")
    print("Two-Way Voice Translation + Ask-Back")
    print("\n1. Hindi to Gujarati")
    print("2. Gujarati to Hindi")
    print("3. Workplace Instruction Ask-Back")
    print("4. Smart Workplace Translation")

    choice = input(
        "\nSelect an option (1, 2, 3, or 4): "
    ).strip()

    if choice not in {"1", "2", "3", "4"}:
        print(
            "Invalid selection. Please choose 1, 2, 3, or 4."
        )
        return

    try:
        validate_config()

        if choice == "1":
            hindi_to_gujarati()

        elif choice == "2":
            gujarati_to_hindi()

        elif choice == "3":
            ask_back()

        elif choice == "4":
            smart_workplace_translation()

    except requests.RequestException as error:
        print(f"\nAPI request failed: {error}")

    except (
        FileNotFoundError,
        ValueError,
        RuntimeError,
    ) as error:
        print(f"\nPipeline failed: {error}")

    except Exception as error:
        print(
            f"\nUnexpected error: {type(error).__name__}: {error}"
        )


if __name__ == "__main__":
    main()