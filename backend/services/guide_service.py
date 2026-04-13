import os
import json
import re
from groq import Groq
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

# Fastest free model for pure JSON generation (no vision needed here)
client = Groq(api_key=os.getenv("GROQ_API_KEY"), timeout=25.0)
TEXT_MODEL = "llama3-8b-8192"

# ─────────────────────────────────────────────────────────
#  HARDCODED GUIDES — instant (no API call), pixel-perfect
# ─────────────────────────────────────────────────────────
HARDCODED_GUIDES = {
    "face": {"subject": "face", "steps": [
        {"type": "circle", "cx": 300, "cy": 200, "r": 130, "label": "Step 1: Big oval — the head"},
        {"type": "arc",    "cx": 170, "cy": 200, "r": 30,  "startAngle": -1.2, "endAngle": 1.2,  "label": "Step 2: Left ear"},
        {"type": "arc",    "cx": 430, "cy": 200, "r": 30,  "startAngle":  1.9, "endAngle": 4.3,  "label": "Step 3: Right ear"},
        {"type": "circle", "cx": 255, "cy": 175, "r": 16,  "label": "Step 4: Left eye"},
        {"type": "circle", "cx": 345, "cy": 175, "r": 16,  "label": "Step 5: Right eye"},
        {"type": "polyline","points": [[295,205],[285,225],[315,225],[305,205]], "label": "Step 6: Nose (triangle)"},
        {"type": "arc",    "cx": 300, "cy": 245, "r": 50,  "startAngle": 0.3,  "endAngle": 2.8,  "label": "Step 7: Smile arc"},
        {"type": "polyline","points": [[265,100],[280,60],[305,70],[325,60],[340,100]], "label": "Step 8: Hair"},
    ]},
    "cat": {"subject": "cat", "steps": [
        {"type": "circle",  "cx": 300, "cy": 200, "r": 110, "label": "Step 1: Round head"},
        {"type": "polyline","points": [[215,120],[202,75],[248,115]],  "label": "Step 2: Left pointed ear"},
        {"type": "polyline","points": [[385,120],[398,75],[352,115]],  "label": "Step 3: Right pointed ear"},
        {"type": "circle",  "cx": 265, "cy": 185, "r": 20,  "label": "Step 4: Left eye"},
        {"type": "circle",  "cx": 335, "cy": 185, "r": 20,  "label": "Step 5: Right eye"},
        {"type": "circle",  "cx": 300, "cy": 218, "r": 11,  "label": "Step 6: Nose (small circle)"},
        {"type": "line",    "x1": 300, "y1": 229, "x2": 300, "y2": 242, "label": "Step 7: Line from nose down"},
        {"type": "arc",     "cx": 284, "cy": 242, "r": 16, "startAngle": 3.14, "endAngle": 6.28, "label": "Step 8: Left mouth curve"},
        {"type": "arc",     "cx": 316, "cy": 242, "r": 16, "startAngle": 3.14, "endAngle": 6.28, "label": "Step 9: Right mouth curve"},
        {"type": "line",    "x1": 205, "y1": 215, "x2": 268, "y2": 218, "label": "Step 10: Left whiskers"},
        {"type": "line",    "x1": 395, "y1": 215, "x2": 332, "y2": 218, "label": "Step 11: Right whiskers"},
    ]},
    "house": {"subject": "house", "steps": [
        {"type": "rect",    "x": 150,  "y": 230, "width": 300, "height": 200, "label": "Step 1: Rectangle — the house body"},
        {"type": "polyline","points": [[130,230],[300,80],[470,230]],            "label": "Step 2: Triangle — the roof"},
        {"type": "rect",    "x": 262,  "y": 330, "width": 76,  "height": 100,  "label": "Step 3: Front door"},
        {"type": "rect",    "x": 175,  "y": 268, "width": 72,  "height": 62,   "label": "Step 4: Left window"},
        {"type": "rect",    "x": 353,  "y": 268, "width": 72,  "height": 62,   "label": "Step 5: Right window"},
        {"type": "line",    "x1": 210, "y1": 267, "x2": 247,   "y2": 267,      "label": "Step 6: Left window cross"},
        {"type": "line",    "x1": 228, "y1": 250, "x2": 228,   "y2": 285,      "label": "Step 7: Left window cross 2"},
        {"type": "rect",    "x": 290,  "y": 30,  "width": 30,  "height": 55,   "label": "Step 8: Chimney"},
    ]},
    "tree": {"subject": "tree", "steps": [
        {"type": "rect",   "x": 272, "y": 300, "width": 56, "height": 140, "label": "Step 1: Trunk rectangle"},
        {"type": "circle", "cx": 300, "cy": 240, "r": 95,  "label": "Step 2: Main foliage (big circle)"},
        {"type": "circle", "cx": 218, "cy": 275, "r": 68,  "label": "Step 3: Left foliage cluster"},
        {"type": "circle", "cx": 382, "cy": 275, "r": 68,  "label": "Step 4: Right foliage cluster"},
        {"type": "circle", "cx": 300, "cy": 165, "r": 58,  "label": "Step 5: Top foliage cluster"},
    ]},
    "star": {"subject": "star", "steps": [
        {"type": "line", "x1": 300, "y1": 70,  "x2": 375, "y2": 350, "label": "Step 1: Right downward line"},
        {"type": "line", "x1": 300, "y1": 70,  "x2": 225, "y2": 350, "label": "Step 2: Left downward line"},
        {"type": "line", "x1": 110, "y1": 165, "x2": 490, "y2": 165, "label": "Step 3: Horizontal line across"},
        {"type": "line", "x1": 110, "y1": 165, "x2": 415, "y2": 375, "label": "Step 4: Bottom-left to bottom-right"},
        {"type": "line", "x1": 490, "y1": 165, "x2": 185, "y2": 375, "label": "Step 5: Bottom-right to bottom-left"},
    ]},
    "sun": {"subject": "sun", "steps": [
        {"type": "circle", "cx": 300, "cy": 225, "r": 80, "label": "Step 1: Circle — the sun body"},
        {"type": "line", "x1": 300, "y1": 90,  "x2": 300, "y2": 55,  "label": "Step 2: Ray — top"},
        {"type": "line", "x1": 300, "y1": 360, "x2": 300, "y2": 395, "label": "Step 3: Ray — bottom"},
        {"type": "line", "x1": 165, "y1": 225, "x2": 130, "y2": 225, "label": "Step 4: Ray — left"},
        {"type": "line", "x1": 435, "y1": 225, "x2": 470, "y2": 225, "label": "Step 5: Ray — right"},
        {"type": "line", "x1": 203, "y1": 122, "x2": 179, "y2": 99,  "label": "Step 6: Ray — top-left diagonal"},
        {"type": "line", "x1": 397, "y1": 122, "x2": 421, "y2": 99,  "label": "Step 7: Ray — top-right diagonal"},
        {"type": "line", "x1": 203, "y1": 328, "x2": 179, "y2": 351, "label": "Step 8: Ray — bottom-left diagonal"},
        {"type": "line", "x1": 397, "y1": 328, "x2": 421, "y2": 351, "label": "Step 9: Ray — bottom-right diagonal"},
    ]},
    "car": {"subject": "car", "steps": [
        {"type": "rect",    "x": 80,  "y": 280, "width": 440, "height": 110, "label": "Step 1: Long rectangle — car body"},
        {"type": "polyline","points": [[155,280],[200,180],[400,180],[450,280]], "label": "Step 2: Trapezoid — car roof/cabin"},
        {"type": "circle",  "cx": 175, "cy": 390, "r": 50, "label": "Step 3: Left wheel (circle)"},
        {"type": "circle",  "cx": 425, "cy": 390, "r": 50, "label": "Step 4: Right wheel (circle)"},
        {"type": "rect",    "x": 210, "y": 193, "width": 80, "height": 75, "label": "Step 5: Left window"},
        {"type": "rect",    "x": 310, "y": 193, "width": 80, "height": 75, "label": "Step 6: Right window"},
    ]},
}

# Subjects we refuse to guide on
INVALID_SUBJECTS = {
    "no subject drawn", "unknown", "nothing", "empty", "blank",
    "none", "n/a", "unclear", "not sure", ""
}

# ─────────────────────────────────────────────────────────
#  AI GUIDE PROMPT (fallback for uncommon subjects)
# ─────────────────────────────────────────────────────────
GUIDE_PROMPT = """You are a drawing teacher. Return ONLY valid JSON.

Canvas: 600 wide, 450 tall. Top-left = (0,0), center = (300,225).

Teach how to draw the given subject using 7-10 simple geometric steps.
Go largest shapes first → then details last.

JSON format (return ONLY this, nothing else):
{
  "subject": "...",
  "steps": [
    {"type": "circle",   "cx": 300, "cy": 200, "r": 110,  "label": "Step 1: ..."},
    {"type": "arc",      "cx": 300, "cy": 240, "r": 50, "startAngle": 0.3, "endAngle": 2.8, "label": "Step 2: ..."},
    {"type": "line",     "x1": 280, "y1": 210, "x2": 320, "y2": 210,       "label": "Step 3: ..."},
    {"type": "rect",     "x": 200,  "y": 300,  "width": 200, "height": 120, "label": "Step 4: ..."},
    {"type": "polyline", "points": [[200,150],[300,80],[400,150]],           "label": "Step 5: ..."}
  ]
}

All x values: 20–580. All y values: 20–430. Output ONLY the JSON."""


def clean_subject(subject: str) -> str:
    return subject.lower().strip().rstrip("s")   # "cats" → "cat"


def get_drawing_guide(subject: str) -> dict:
    cleaned = clean_subject(subject)

    # 1. Reject bad subjects
    if cleaned in INVALID_SUBJECTS or len(cleaned) < 2:
        raise ValueError(f"Cannot generate a guide for '{subject}'. Please type a real subject like 'cat' or 'house'.")

    # 2. Instant hardcoded guide (no API call needed)
    for key, guide in HARDCODED_GUIDES.items():
        if key in cleaned or cleaned in key:
            return guide

    # 3. AI fallback for unusual subjects
    response = client.chat.completions.create(
        model=TEXT_MODEL,
        messages=[
            {"role": "system", "content": GUIDE_PROMPT},
            {"role": "user",   "content": f"Teach me how to draw: {subject}"},
        ],
        max_tokens=900,
        temperature=0.2,
        response_format={"type": "json_object"},
    )
    content = response.choices[0].message.content
    return _extract_json(content, subject)


def _extract_json(text: str, subject: str) -> dict:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
    return {"subject": subject, "steps": []}
