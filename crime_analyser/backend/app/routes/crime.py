from fastapi import APIRouter, Query, HTTPException
from app.services.crime_query import get_crime_data, get_all_categories, get_overview

router = APIRouter()


@router.get("/api/crime/overview")
async def overview(postcode: str = Query(...)):
    data = get_overview(postcode)
    if not data:
        raise HTTPException(404, "No data for that postcode")
    return data


@router.get("/api/crime")
async def crime(postcode: str = Query(...), category: str = Query(...)):
    data = get_crime_data(postcode, category)
    if not data:
        raise HTTPException(404, "No data for that postcode/category")
    return data


@router.get("/api/categories")
async def categories():
    return get_all_categories()
