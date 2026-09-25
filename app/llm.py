from __future__ import annotations

import json
import random
import time

from google import genai
from google.genai import types

from .config import settings
from .models import ChangePlan


SYSTEM_PROMPT = """
You are CodeForge, an autonomous coding agent operating on a sandboxed project workspace.

Your job:
1. Inspect the supplied workspace snapshot.
2. Understand the user's coding task.
3. Produce the smallest coherent set of file changes needed.
4. Preserve existing behavior unless the task requires changing it.
5. Add or update tests when reasonable.
6. Suggest only validation commands from this allowlist:
   - python -m pytest
   - pytest
   - python -m compileall .
   - python -m unittest

Security and quality rules:
- Never modify files outside the workspace.
- Never request secrets.
- Never create malware, credential theft, persistence, destructive code, or unsafe shell commands.
- Do not use placeholders such as TODO.
- Return complete file content for every create/update action.
- Prefer simple, readable, maintainable code.
- If a file should be deleted, set action to "delete" and content to null.
- Keep validation commands restricted to the approved allowlist.
- Return JSON only.
- Do not wrap the JSON in markdown fences.

Return JSON matching exactly this shape:

{
  "summary": "short plan summary",
  "changes": [
    {
      "path": "relative/path.ext",
      "action": "create|update|delete",
      "content": "complete file contents or null",
      "reason": "why this change is needed"
    }
  ],
  "validation_commands": [
    "python -m pytest"
  ]
}
"""


def _extract_json(text: str) -> dict:
    """
    Extract and parse JSON returned by Gemini.

    Gemini is instructed to return application/json, but this helper
    makes the parser more tolerant in case extra text is returned.
    """
    if not text:
        raise ValueError("Gemini returned an empty response.")

    text = text.strip()

    if text.startswith("```"):
        text = text.strip("`").strip()

        if text.lower().startswith("json"):
            text = text[4:].strip()

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1 or end <= start:
        raise ValueError(
            f"Gemini did not return valid JSON.\nRaw response:\n{text[:2000]}"
        )

    json_text = text[start : end + 1]

    try:
        return json.loads(json_text)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Gemini returned malformed JSON.\n"
            f"JSON error: {exc}\n"
            f"Raw response:\n{text[:2000]}"
        ) from exc


def _generate_with_retry(
    client: genai.Client,
    user_prompt: str,
):
    """
    Call Gemini with exponential backoff.

    This helps recover from temporary:
    - 503 high-demand errors
    - transient network errors
    - temporary provider failures
    """

    max_attempts = 5
    last_error: Exception | None = None

    for attempt in range(1, max_attempts + 1):
        try:
            response = client.models.generate_content(
                model=settings.gemini_model,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.2,
                    response_mime_type="application/json",
                ),
            )

            return response

        except Exception as exc:
            last_error = exc

            if attempt >= max_attempts:
                break

            # Exponential backoff:
            # ~2s, ~4s, ~8s, ~16s
            wait_seconds = (2 ** attempt) + random.uniform(0.0, 1.5)

            print(
                f"[CodeForge] Gemini request failed "
                f"(attempt {attempt}/{max_attempts}). "
                f"Retrying in {wait_seconds:.1f}s..."
            )

            time.sleep(wait_seconds)

    raise RuntimeError(
        f"Gemini request failed after {max_attempts} attempts.\n"
        f"Last error: {last_error}"
    ) from last_error


def make_plan(
    task: str,
    snapshot: str,
    feedback: str = "",
) -> ChangePlan:
    """
    Ask Gemini to produce the next coding plan.

    The agent receives:
    - the user's task
    - the current workspace
    - validation output from the previous iteration

    It returns a validated ChangePlan object.
    """

    if not settings.gemini_api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. "
            "Add it to the .env file and restart CodeForge."
        )

    client = genai.Client(
        api_key=settings.gemini_api_key
    )

    user_prompt = f"""
USER TASK:
{task}

CURRENT WORKSPACE:
{snapshot}

VALIDATION FEEDBACK FROM THE PREVIOUS ATTEMPT:
{feedback or "[none]"}

INSTRUCTIONS:

Generate the next implementation plan.

If validation previously failed:
1. inspect the failure
2. identify the cause
3. correct the implementation
4. return complete updated file contents

Do not provide explanations outside the JSON response.

The response must contain:
- summary
- changes
- validation_commands
"""

    response = _generate_with_retry(
        client=client,
        user_prompt=user_prompt,
    )

    if not response.text:
        raise RuntimeError(
            "Gemini returned an empty response."
        )

    data = _extract_json(response.text)

    try:
        plan = ChangePlan.model_validate(data)
    except Exception as exc:
        raise ValueError(
            "Gemini returned JSON, but it did not match "
            "the expected CodeForge plan schema.\n\n"
            f"Response:\n{json.dumps(data, indent=2)}"
        ) from exc

    return plan