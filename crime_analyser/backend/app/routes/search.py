from fastapi import APIRouter, Query
from app.services.crime_query import search_postcodes

router = APIRouter()


@router.get("/suggest")
async def suggest(q: str = Query(..., min_length=1)):
    return search_postcodes(q)
