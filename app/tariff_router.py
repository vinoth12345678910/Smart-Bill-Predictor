# app/tariff_router.py

from fastapi import APIRouter, Query
from app.tariff_links import get_tariff_link

router = APIRouter(prefix="/tariff", tags=["Tariff Links"])

@router.get("/link")
def tariff_link(state: str = Query(..., description="Enter full state or UT name")):
    url = get_tariff_link(state)
    if url:
        return {"state": state.strip().title(), "tariff_link": url}
    return {"error": f"No tariff URL configured for '{state}'."}
