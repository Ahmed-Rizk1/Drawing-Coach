from fastapi import APIRouter, HTTPException
from models.schemas import GuideRequest, GuideResponse
from services.guide_service import get_drawing_guide

router = APIRouter()

@router.post("/guide", response_model=GuideResponse)
async def guide(request: GuideRequest):
    if not request.subject or not request.subject.strip():
        raise HTTPException(status_code=400, detail="Subject is required.")
    try:
        result = get_drawing_guide(request.subject.strip())
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    if not result.get("steps"):
        raise HTTPException(status_code=500, detail="Could not generate guide steps.")

    return GuideResponse(**result)
