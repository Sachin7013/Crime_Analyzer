from pydantic import BaseModel


class PostcodeSuggestion(BaseModel):
    postcode: str
    place: str


class TrendInfo(BaseModel):
    direction: str
    pct_change_5yr: int


class YearlyTotal(BaseModel):
    year: int
    total: int


class SubcategoryData(BaseModel):
    name: str
    monthly: list[int]


class CrimeResponse(BaseModel):
    postcode: str
    place: str
    category: str
    monthly: list[int]
    yearly: list[YearlyTotal]
    total: int
    last_year_total: int
    trend: TrendInfo
    subcategories: list[SubcategoryData]


class CategoryInfo(BaseModel):
    category: str
    subcategories: list[str]


class GeometryResponse(BaseModel):
    postcode: str
    centroid: list[float]
    boundary: dict | None = None


class HealthResponse(BaseModel):
    status: str
