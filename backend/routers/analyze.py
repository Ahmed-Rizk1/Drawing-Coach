from fastapi import APIRouter, HTTPException
from models.schemas import AnalyzeRequest, AnalyzeResponse
from services.ai_service import analyze_drawing

router = APIRouter()

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest):
    """
    Receives a base64-encoded drawing image from the frontend.
    Returns description, guess, and improvement tips.
    """
    if not request.image:
        raise HTTPException(status_code=400, detail="No image data received.")

    result = analyze_drawing(request.image)
    return AnalyzeResponse(**result)
