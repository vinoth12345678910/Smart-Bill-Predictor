from __future__ import annotations

from fastapi import APIRouter, Query
from pydantic import BaseModel

from app.tariff_engine import TariffEngine, TariffContext


router = APIRouter(prefix="/dynamic-tariff", tags=["Dynamic Tariff Engine"])


class BillRequest(BaseModel):
    state: str
    category: str = "domestic"
    units: float
    season: str | None = None
    time_of_day: str | None = None


engine = TariffEngine()


@router.post("/compute")
def compute_bill(payload: BillRequest):
    context = TariffContext(
        state=payload.state,
        category=payload.category,
        season=payload.season,
        time_of_day=payload.time_of_day,
    )
    result = engine.compute_bill(units=payload.units, context=context)
    return result


@router.get("/table")
def get_table(state: str = Query(...), category: str = Query("domestic")):
    try:
        return engine.get_tariff_table(state=state, category=category)
    except Exception as e:
        return {"error": str(e), "state": state, "category": category}


