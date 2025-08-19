# app/tariff_data.py

TARIFF_DATA = {
    # --- States with verified slab data ---
    "Tamil Nadu": {
        "category": "domestic",
        "slabs": [
            {"upto": 100, "rate": 0.00},
            {"upto": 200, "rate": 2.35},
            {"upto": 400, "rate": 4.70},
            {"upto": 500, "rate": 6.30},
            {"upto": 600, "rate": 8.40},
            {"upto": 800, "rate": 9.45},
            {"upto": 1000, "rate": 10.50},
            {"above": 1000, "rate": 11.55}
        ]
    },
    "Delhi": {
        "category": "domestic",
        "slabs": [
            {"upto": 200, "rate": 0.00},
            {"upto": 400, "rate": 3.00},
            {"upto": 800, "rate": 6.50},
            {"upto": 1200, "rate": 7.00},
            {"above": 1200, "rate": 8.00}
        ]
    },

    # --- States with average rates only ---
    "Maharashtra": {"category": "domestic", "average_rate": 6.85},
    "Punjab": {"category": "domestic", "average_rate": 6.00},
    "Uttar Pradesh": {"category": "domestic", "average_rate": 7.10},
    "Haryana": {"category": "domestic", "average_rate": 6.00},
    "Bihar": {"category": "domestic", "average_rate": 6.75},
    "Rajasthan": {"category": "domestic", "average_rate": 6.29},
    "Gujarat": {"category": "domestic", "average_rate": 6.00},
    "West Bengal": {"category": "domestic", "average_rate": 6.50},
    "Kerala": {"category": "domestic", "average_rate": 6.05},
    "Karnataka": {"category": "domestic", "average_rate": 6.15},
    "Andhra Pradesh": {"category": "domestic", "average_rate": 6.40},
    "Telangana": {"category": "domestic", "average_rate": 6.45},
    "Madhya Pradesh": {"category": "domestic", "average_rate": 6.55},
    "Chhattisgarh": {"category": "domestic", "average_rate": 6.30},
    "Odisha": {"category": "domestic", "average_rate": 6.20},
    "Jharkhand": {"category": "domestic", "average_rate": 6.35},
    "Assam": {"category": "domestic", "average_rate": 6.10},
    "Meghalaya": {"category": "domestic", "average_rate": 6.00},
    "Tripura": {"category": "domestic", "average_rate": 6.05},
    "Mizoram": {"category": "domestic", "average_rate": 6.00},
    "Manipur": {"category": "domestic", "average_rate": 6.05},
    "Nagaland": {"category": "domestic", "average_rate": 6.10},
    "Sikkim": {"category": "domestic", "average_rate": 6.20},
    "Arunachal Pradesh": {"category": "domestic", "average_rate": 6.15},
    "Goa": {"category": "domestic", "average_rate": 6.25},
    "Himachal Pradesh": {"category": "domestic", "average_rate": 6.00},
    "Uttarakhand": {"category": "domestic", "average_rate": 6.05},
    "Jammu & Kashmir": {"category": "domestic", "average_rate": 6.10}
}
