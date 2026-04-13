import os
import json
import base64
import io
import re
from groq import Groq
from PIL import Image
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

# ── Timeout added: fail fast instead of hanging forever ──
client = Groq(api_key=os.getenv("GROQ_API_KEY"), timeout=30.0)

VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

SYSTEM_PROMPT = """You are an encouraging AI drawing coach and art mentor.

Analyze the drawing and respond ONLY with this JSON:
{
  "description": "What you see in the drawing (2-3 sentences)",
  "guess": "Your best guess of the subject in 1 short phrase",
  "tips": ["specific tip 1", "specific tip 2", "specific tip 3"]
}

Be warm and constructive. Output ONLY the JSON object."""


def compress_image(image_b64: str) -> str:
    """
    Resize + convert to JPEG before sending to Groq.
    CRITICAL: Canvas exports as transparent PNG. We must composite
    on a white background FIRST, otherwise transparent → black in JPEG
    and the AI sees a completely black image.
    """
    image_bytes = base64.b64decode(image_b64)
    image = Image.open(io.BytesIO(image_bytes)).convert("RGBA")

    # Create white background and paste drawing on top using alpha mask
    white_bg = Image.new("RGBA", image.size, (255, 255, 255, 255))
    white_bg.paste(image, mask=image.split()[3])   # [3] = alpha channel
    rgb_image = white_bg.convert("RGB")

    # Resize to reduce payload
    rgb_image.thumbnail((512, 384), Image.LANCZOS)
    buffer = io.BytesIO()
    rgb_image.save(buffer, format="JPEG", quality=85)
    return base64.b64encode(buffer.getvalue()).decode()


def extract_json(text: str) -> dict:
    """
    Safely extract JSON from the model's response.
    Handles cases where the model adds extra text before/after the JSON.
    """
    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to find a JSON block inside the text
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    # Fallback
    return {
        "description": text[:200] if text else "Could not analyze the drawing.",
        "guess": "Unknown",
        "tips": ["Try drawing with more contrast", "Keep practicing!"],
    }


def analyze_drawing(image_b64: str) -> dict:
    """
    Sends the compressed drawing to Groq's vision model.
    Returns a dict with description, guess, and tips.
    """
    # Strip "data:image/...;base64," prefix if present
    if "," in image_b64:
        image_b64 = image_b64.split(",")[1]

    # ── Compress before sending ──
    compressed = compress_image(image_b64)

    response = client.chat.completions.create(
        model=VISION_MODEL,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{compressed}"
                        },
                    },
                    {
                        "type": "text",
                        "text": "Analyze this drawing and give coaching feedback.",
                    },
                ],
            },
        ],
        max_tokens=512,
        temperature=0.7,
        # NOTE: response_format removed — not supported for vision on all models
    )

    content = response.choices[0].message.content
    return extract_json(content)
