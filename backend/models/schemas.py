from pydantic import BaseModel
from typing import List, Optional

# ── Analyze ──
class AnalyzeRequest(BaseModel):
    image: str  # base64 PNG

class AnalyzeResponse(BaseModel):
    description: str
    guess: str
    tips: List[str]

# ── Guide ──
class GuideRequest(BaseModel):
    subject: str  # e.g. "face", "cat", "house"

class GuideStep(BaseModel):
    type: str          # "circle" | "line" | "rect" | "arc" | "polyline"
    label: str         # Human-readable instruction shown to user
    # circle / arc
    cx: Optional[float] = None
    cy: Optional[float] = None
    r: Optional[float] = None
    startAngle: Optional[float] = None   # radians, arc only
    endAngle: Optional[float] = None     # radians, arc only
    # line
    x1: Optional[float] = None
    y1: Optional[float] = None
    x2: Optional[float] = None
    y2: Optional[float] = None
    # rect
    x: Optional[float] = None
    y: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    # polyline
    points: Optional[List[List[float]]] = None  # [[x,y], [x,y], ...]

class GuideResponse(BaseModel):
    subject: str
    steps: List[GuideStep]
