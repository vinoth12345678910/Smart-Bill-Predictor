from __future__ import annotations

import datetime as _dt
import json
import os
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from app.tariff_cache import get_cache, CacheInterface


# ---------- Data source ----------

DEFAULT_TARIFF_JSON_PATH = os.path.join(os.path.dirname(__file__), "tariffs.json")


def _load_tariff_json(path: str) -> Dict[str, dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ---------- Models ----------

@dataclass
class TariffContext:
    state: str
    category: str  # e.g., "domestic", "commercial"
    season: Optional[str] = None  # e.g., "summer", "monsoon", "winter"
    time_of_day: Optional[str] = None  # e.g., "peak", "off_peak", "mid"


@dataclass
class SlabLine:
    upto: Optional[float]  # None means no upper bound
    rate: float


# ---------- Engine ----------

class TariffEngine:
    def __init__(self, json_path: Optional[str] = None, cache: Optional[CacheInterface] = None) -> None:
        self.json_path = json_path or DEFAULT_TARIFF_JSON_PATH
        self.cache = cache or get_cache()

    # Public API
    def get_tariff_table(self, state: str, category: str) -> dict:
        cache_key = f"tariff_table::{os.path.abspath(self.json_path)}::{state.lower()}::{category.lower()}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached

        all_tariffs = _load_tariff_json(self.json_path)
        state_data = all_tariffs.get(state) or all_tariffs.get(state.title()) or all_tariffs.get(state.upper())
        if not state_data:
            raise ValueError(f"No tariff data for state '{state}'.")

        category_data = state_data.get(category) or state_data.get(category.title()) or state_data.get(category.lower())
        if not category_data:
            raise ValueError(f"No tariff data for state '{state}' and category '{category}'.")

        self.cache.set(cache_key, category_data, ttl_seconds=3600)
        return category_data

    def compute_bill(self, units: float, context: TariffContext) -> Dict[str, float]:
        table = self.get_tariff_table(context.state, context.category)

        # Select season and ToD modifiers
        season_factor = self._resolve_season_factor(table, context.season)
        tod_factor = self._resolve_tod_factor(table, context.time_of_day)

        slabs = self._parse_slabs(table.get("slabs", []))
        if not slabs and "flat_rate" in table:
            base_amount = units * float(table["flat_rate"])
        else:
            base_amount = self._compute_slab_amount(units, slabs)

        adjusted_amount = base_amount * season_factor * tod_factor
        fixed_charge = float(table.get("fixed_charge", 0.0))
        total_amount = adjusted_amount + fixed_charge
        return {
            "units": float(units),
            "base_amount": round(base_amount, 2),
            "season_factor": round(season_factor, 4),
            "tod_factor": round(tod_factor, 4),
            "fixed_charge": round(fixed_charge, 2),
            "total_amount": round(total_amount, 2),
        }

    # ---------- Internals ----------
    @staticmethod
    def _parse_slabs(slab_rows: List[dict]) -> List[SlabLine]:
        parsed: List[SlabLine] = []
        upper_seen: List[float] = []
        for row in slab_rows:
            if "above" in row:
                parsed.append(SlabLine(upto=None, rate=float(row["rate"])) )
            elif "upto" in row:
                upto_value = float(row["upto"])
                # skip duplicates
                if upper_seen and upto_value <= max(upper_seen):
                    continue
                upper_seen.append(upto_value)
                parsed.append(SlabLine(upto=upto_value, rate=float(row["rate"])) )
        return parsed

    @staticmethod
    def _compute_slab_amount(units: float, slabs: List[SlabLine]) -> float:
        remaining = float(units)
        billed = 0.0
        last_upper = 0.0
        for slab in slabs:
            if slab.upto is None:
                billed += remaining * slab.rate
                remaining = 0.0
                break
            span = max(0.0, min(remaining, slab.upto - last_upper))
            billed += span * slab.rate
            remaining -= span
            last_upper = slab.upto
            if remaining <= 0.0:
                break
        # If units extend beyond last explicit slab but no 'above' given, apply last rate
        if remaining > 0.0 and slabs:
            billed += remaining * slabs[-1].rate
        return billed

    @staticmethod
    def _resolve_season_factor(table: dict, season: Optional[str]) -> float:
        mapping = table.get("season_multipliers", {})
        if not mapping:
            return 1.0
        if not season:
            # autodetect by calendar if provided
            month = _dt.datetime.utcnow().month
            season = TariffEngine._infer_season_by_month(month, mapping)
        # If no season mapping or season is "default", return 1.0
        if season == "default" or not season:
            return 1.0
        key = TariffEngine._case_insensitive_key(mapping, season)
        if key is None:
            return 1.0
        return float(mapping[key])

    @staticmethod
    def _resolve_tod_factor(table: dict, time_of_day: Optional[str]) -> float:
        mapping = table.get("time_of_day_multipliers", {})
        if not mapping:
            return 1.0
        if not time_of_day:
            # default bucket
            time_of_day = "mid"
        key = TariffEngine._case_insensitive_key(mapping, time_of_day)
        if key is None:
            return 1.0
        return float(mapping[key])

    @staticmethod
    def _case_insensitive_key(mapping: dict, key: Optional[str]) -> Optional[str]:
        if key is None:
            return None
        for k in mapping.keys():
            if k.lower() == key.lower():
                return k
        return None

    @staticmethod
    def _infer_season_by_month(month: int, mapping: dict) -> str:
        # Heuristic: Apr-Jun summer, Jul-Sep monsoon, Oct-Feb winter, Mar shoulder -> default 1.0
        if any(k.lower() == "summer" for k in mapping):
            if 4 <= month <= 6:
                return "summer"
        if any(k.lower() == "monsoon" for k in mapping):
            if 7 <= month <= 9:
                return "monsoon"
        if any(k.lower() == "winter" for k in mapping):
            if month in (10, 11, 12, 1, 2):
                return "winter"
        # Return first available season or default to first key if mapping is not empty
        return next(iter(mapping.keys())) if mapping else "default"


__all__ = [
    "TariffEngine",
    "TariffContext",
]


