"""
logic.py — data layer and validation for Weather Diary.
Separated from the GUI so unit tests can run without tkinter.
"""

import json
import os
from datetime import datetime

DATA_FILE = "weather_data.json"


# ─────────────────────────── data layer ───────────────────────────

def load_records() -> list[dict]:
    """Load records from JSON file. Returns empty list if file doesn't exist."""
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_records(records: list[dict]) -> None:
    """Save records list to JSON file."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


# ─────────────────────────── validation ───────────────────────────

def validate_date(date_str: str) -> bool:
    """Return True if date_str matches DD.MM.YYYY format."""
    try:
        datetime.strptime(date_str.strip(), "%d.%m.%Y")
        return True
    except ValueError:
        return False


def validate_temperature(temp_str: str) -> bool:
    """Return True if temp_str can be parsed as a float."""
    try:
        float(temp_str.strip())
        return True
    except ValueError:
        return False


# ─────────────────────────── filtering ───────────────────────────

def filter_records(
    records: list[dict],
    date_filter: str = "",
    temp_filter: str = "",
) -> list[dict]:
    """
    Return a filtered copy of records.

    date_filter  — exact date string DD.MM.YYYY (empty = no filter)
    temp_filter  — minimum temperature threshold as string (empty = no filter)
    """
    result = records
    if date_filter:
        result = [r for r in result if r["date"] == date_filter]
    if temp_filter:
        threshold = float(temp_filter)
        result = [r for r in result if r["temperature"] > threshold]
    return result
