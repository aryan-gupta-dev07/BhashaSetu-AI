import json
import requests

from config import GROQ_API_KEY, GROQ_MODEL, GROQ_URL


def check_instruction_clarity(instruction, language="Hindi", conversation_context=None):
    # Validate input
    if not isinstance(instruction, str) or not instruction.strip():
        raise ValueError("Instruction cannot be empty.")

    if not isinstance(language, str) or not language.strip():
        raise ValueError("Language cannot be empty.")
    
    if conversation_context is not None:
        if not isinstance(conversation_context, str):
            raise ValueError("Conversation context must be a string.")

        if len(conversation_context) > 3000:
            raise ValueError("Conversation context is too long.")

    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY is missing.")
    

    prompt = f"""
You are a workplace instruction clarity checker.

Analyze this instruction in {language}.

Previous conversation context:
{conversation_context if conversation_context else "No previous context provided."}

Use the previous context only when it is relevant to the current instruction.
If the current instruction refers to an earlier task, interpret it using that context.
Never assume details that are not present in the instruction or context.
If important information is still missing, ask one specific clarification question.
If the current instruction conflicts with a previous instruction in the conversation context, set status to NEEDS_CLARIFICATION.
Explain the conflict briefly and ask which instruction should be followed.
Never silently choose one of the conflicting instructions.

Rules:
1. Check whether the instruction includes enough information to act correctly.
2. Words like "soon", "ASAP", "as quickly as possible",
   and "when possible" may indicate a missing deadline.
3. If the task is identifiable but the deadline is missing,
   ask for a specific deadline, not what the task is.
4. If the task itself is unclear, ask what specific action is required.
5. Do not ask unnecessary questions when the instruction is already clear.
6. Never invent missing details.
7. Return only valid JSON. Do not use markdown code fences.

Use exactly this JSON structure:
{{
    "status": "CLEAR or NEEDS_CLARIFICATION",
    "reason": "Brief explanation",
    "question": "One relevant question, or null"
}}

Instruction: {instruction.strip()}
"""

    try:
        response = requests.post(
            GROQ_URL,
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": GROQ_MODEL,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0,
            },
            timeout=60,
        )

        response.raise_for_status()

        content = response.json()["choices"][0]["message"]["content"]
        result = json.loads(content)

    except requests.RequestException as error:
        raise RuntimeError(f"API request failed: {error}") from error

    except (ValueError, KeyError, IndexError, TypeError) as error:
        raise RuntimeError("Invalid API response.") from error

    # Validate the response structure
    if not isinstance(result, dict):
        raise RuntimeError("Invalid clarification response format.")

    # Validate status
    if result.get("status") not in {
        "CLEAR",
        "NEEDS_CLARIFICATION",
    }:
        raise RuntimeError("Invalid clarification status.")

    # Validate reason
    reason = result.get("reason")

    if not isinstance(reason, str) or not reason.strip():
        raise RuntimeError("Invalid reason in API response.")

    # Validate clarification question
    if result["status"] == "NEEDS_CLARIFICATION":
        question = result.get("question")

        if not isinstance(question, str) or not question.strip():
            raise RuntimeError("Clarification question is missing.")

    else:
        result["question"] = None

    return result