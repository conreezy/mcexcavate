from __future__ import annotations

import base64
import mimetypes
import os
import time
from typing import Any, Optional

import requests

OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"
DEFAULT_MODEL = os.getenv("OPENAI_ALT_TEXT_MODEL", "gpt-4.1")
DEFAULT_DETAIL = os.getenv("OPENAI_ALT_TEXT_DETAIL", "high")
DEFAULT_TIMEOUT = int(os.getenv("OPENAI_ALT_TEXT_TIMEOUT", "60"))
DEFAULT_MAX_RETRIES = int(os.getenv("OPENAI_ALT_TEXT_MAX_RETRIES", "4"))
DEFAULT_RETRY_BACKOFF = float(os.getenv("OPENAI_ALT_TEXT_RETRY_BACKOFF", "2.0"))
ALT_TEXT_PROMPT = (
    "Write one concise SEO-friendly HTML alt attribute for this image. "
    "Describe only what is clearly visible. "
    "Prefer specific construction details when present, such as stamped concrete, driveway, walkway, patio, steps, excavation equipment, or crew activity. "
    "Do not keyword stuff. Do not mention SEO. Do not start with 'image of' or 'photo of'. "
    "Return only the alt text, with no quotes, labels, or extra commentary."
)


class AltTextGenerationError(RuntimeError):
    pass


def _guess_mime_type(filename: str) -> str:
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type or "image/jpeg"


def _extract_output_text(payload: dict[str, Any]) -> str:
    for item in payload.get("output", []):
        if item.get("type") != "message":
            continue
        for content in item.get("content", []):
            if content.get("type") == "output_text":
                text = (content.get("text") or "").strip()
                if text:
                    return text

    text = (payload.get("output_text") or "").strip()
    if text:
        return text

    raise AltTextGenerationError("OpenAI response did not include alt text output.")


def generate_alt_text_for_image_file(
    image_file,
    *,
    model: Optional[str] = None,
    detail: Optional[str] = None,
    timeout: Optional[int] = None,
    max_retries: Optional[int] = None,
    retry_backoff: Optional[float] = None,
) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise AltTextGenerationError("OPENAI_API_KEY is not set.")

    file_name = getattr(image_file, "name", "image.jpg")
    image_file.seek(0)
    image_bytes = image_file.read()
    image_file.seek(0)

    if not image_bytes:
        raise AltTextGenerationError(f"Image file '{file_name}' is empty.")

    mime_type = _guess_mime_type(file_name)
    encoded_image = base64.b64encode(image_bytes).decode("utf-8")
    image_data_url = f"data:{mime_type};base64,{encoded_image}"

    payload = {
        "model": model or DEFAULT_MODEL,
        "input": [
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": ALT_TEXT_PROMPT},
                    {
                        "type": "input_image",
                        "image_url": image_data_url,
                        "detail": detail or DEFAULT_DETAIL,
                    },
                ],
            }
        ],
    }

    retries = DEFAULT_MAX_RETRIES if max_retries is None else max_retries
    backoff = DEFAULT_RETRY_BACKOFF if retry_backoff is None else retry_backoff
    request_timeout = timeout or DEFAULT_TIMEOUT

    for attempt in range(retries + 1):
        try:
            response = requests.post(
                OPENAI_RESPONSES_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=request_timeout,
            )

            if response.status_code in {429, 500, 502, 503, 504} and attempt < retries:
                time.sleep(backoff * (attempt + 1))
                continue

            response.raise_for_status()
            alt_text = _extract_output_text(response.json())
            return alt_text.strip()
        except requests.HTTPError as exc:
            if attempt < retries and response.status_code in {429, 500, 502, 503, 504}:
                time.sleep(backoff * (attempt + 1))
                continue
            raise AltTextGenerationError(
                f"OpenAI alt text request failed for '{file_name}': {response.text}"
            ) from exc
        except requests.RequestException as exc:
            if attempt < retries:
                time.sleep(backoff * (attempt + 1))
                continue
            raise AltTextGenerationError(
                f"OpenAI alt text request failed for '{file_name}': {exc}"
            ) from exc

    raise AltTextGenerationError(f"OpenAI alt text request failed for '{file_name}' after retries.")
