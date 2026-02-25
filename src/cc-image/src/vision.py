"""GPT-4 Vision: image analysis and OCR."""

import base64
import os
from pathlib import Path

import requests


def get_api_key() -> str:
    """Get OpenAI API key from environment."""
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY environment variable not set")
    return key


def encode_image(path: Path) -> str:
    """Encode image to base64."""
    return base64.b64encode(path.read_bytes()).decode("utf-8")


def get_media_type(path: Path) -> str:
    """Get MIME type for image."""
    types = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".gif": "image/gif", ".webp": "image/webp"}
    return types.get(path.suffix.lower(), "image/jpeg")


def vision(image_path: Path, prompt: str, model: str = "gpt-4o", max_tokens: int = 1000) -> str:
    """Analyze image with GPT-4 Vision."""
    image_path = Path(image_path)
    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    b64 = encode_image(image_path)
    media = get_media_type(image_path)

    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {get_api_key()}",
        },
        json={
            "model": model,
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:{media};base64,{b64}"}}
                ]
            }],
            "max_tokens": max_tokens,
        },
        timeout=60,
    )

    if response.status_code != 200:
        raise RuntimeError(f"Vision API error: {response.text}")

    return response.json()["choices"][0]["message"]["content"]


def describe(image_path: Path) -> str:
    """Get detailed description of an image."""
    return vision(
        image_path,
        "Describe this image in detail. Include subjects, colors, composition, mood, and notable elements."
    )


def extract_text(image_path: Path) -> str:
    """Extract text from image (OCR)."""
    return vision(
        image_path,
        "Extract and return all text visible in this image. Return only the text, nothing else."
    )
