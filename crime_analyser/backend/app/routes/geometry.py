from fastapi import APIRouter, Query, HTTPException
from app.services.crime_query import get_geometry

router = APIRouter()


@router.get("/api/geometry")
async def geometry(postcode: str = Query(...)):
    data = get_geometry(postcode)
    if not data:
        raise HTTPException(404, "No geometry for that postcode")
    return data
