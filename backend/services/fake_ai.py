import base64
import io
from PIL import Image

def analyze_drawing(image_b64: str) -> dict:
    """
    Fake AI: analyzes the image using basic pixel-level stats.
    We'll replace this with a real vision model later.
    """
    # ── Step 1: Decode base64 → real image ──
    # Strip the "data:image/png;base64," prefix if present
    if "," in image_b64:
        image_b64 = image_b64.split(",")[1]

    image_bytes = base64.b64decode(image_b64)
    image = Image.open(io.BytesIO(image_bytes)).convert("RGBA")

    # ── Step 2: Count non-white (drawn) pixels ──
    pixels = list(image.getdata())
    drawn = sum(1 for r, g, b, a in pixels if a > 10)  # non-transparent pixels
    total = len(pixels)
    coverage = drawn / total  # 0.0 → 1.0

    # ── Step 3: Guess based on coverage ──
    if coverage < 0.01:
        guess = "Nothing drawn yet! 👀"
        description = "The canvas appears to be empty or nearly blank."
        tips = ["Try drawing a simple shape like a circle or square first!"]

    elif coverage < 0.05:
        guess = "A simple shape (circle, line, or dot)"
        description = f"A minimal drawing covering about {coverage*100:.1f}% of the canvas."
        tips = [
            "Add more details to fill the canvas",
            "Try adding shading or texture",
            "Consider a background",
        ]

    elif coverage < 0.20:
        guess = "A sketch or simple object"
        description = f"A light sketch covering {coverage*100:.1f}% of the canvas."
        tips = [
            "Great start! Try adding outlines",
            "Vary your line thickness for depth",
            "Add a focal point to guide the eye",
        ]

    else:
        guess = "A detailed drawing or full scene"
        description = f"A detailed composition using {coverage*100:.1f}% of the canvas."
        tips = [
            "Excellent coverage! Consider adding contrast",
            "Try using lighter strokes for highlights",
            "Balance busy areas with negative space",
        ]

    return {
        "description": description,
        "guess": guess,
        "tips": tips,
    }
