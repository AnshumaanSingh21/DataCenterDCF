"""
TTL-based cache for market intelligence LLM responses.

Storage : outputs/market_cache.json
Key     : "{location}|{facility_type}"
TTL     : 90 days (configurable via CACHE_TTL_DAYS)

Each cache entry stores:
  - fetched_at  : ISO-8601 timestamp of when the LLM was called
  - llm_raw     : raw parsed JSON from the LLM (pre-validation)
  - audit       : validation audit log (list of dicts)
  - overrides   : the validated assumption overrides ready to inject into engines
"""

import json
import os
from datetime import datetime, timezone, timedelta
from copy import deepcopy

CACHE_PATH    = os.path.join(
    os.path.dirname(__file__), "..", "..", "outputs", "market_cache.json"
)
CACHE_TTL_DAYS = 90


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _cache_key(location: str, facility_type: str, kw_per_rack: float) -> str:
    return f"{location}|{facility_type}|{round(kw_per_rack, 1)}kw"


def _load() -> dict:
    path = os.path.abspath(CACHE_PATH)
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _save(data: dict) -> None:
    path = os.path.abspath(CACHE_PATH)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _is_fresh(entry: dict, ttl_days: int = CACHE_TTL_DAYS) -> bool:
    fetched_at = entry.get("fetched_at")
    if not fetched_at:
        return False
    try:
        ts = datetime.fromisoformat(fetched_at)
        age = datetime.now(timezone.utc) - ts
        return age < timedelta(days=ttl_days)
    except (ValueError, TypeError):
        return False


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get(location: str, facility_type: str, kw_per_rack: float = 6.0) -> dict | None:
    """
    Return cached entry if it exists and is within TTL.
    Returns None if missing or stale.

    Entry structure:
      {
        "fetched_at"  : str,
        "location"    : str,
        "facility_type": str,
        "llm_raw"     : dict,
        "audit"       : list,
        "overrides"   : dict,   # validated assumption overrides per engine
        "age_days"    : float,  # computed on read, not stored
      }
    """
    cache = _load()
    key   = _cache_key(location, facility_type, kw_per_rack)
    entry = cache.get(key)

    if entry is None:
        return None

    if not _is_fresh(entry):
        return None

    result = deepcopy(entry)
    try:
        ts  = datetime.fromisoformat(entry["fetched_at"])
        age = datetime.now(timezone.utc) - ts
        result["age_days"] = round(age.total_seconds() / 86400, 1)
    except Exception:
        result["age_days"] = None

    return result


def set(
    location: str,
    facility_type: str,
    kw_per_rack: float,
    llm_raw: dict,
    audit: list,
    overrides: dict,
) -> None:
    """
    Store a validated LLM response in the cache.

    overrides: dict with keys "revenue", "capex", "loan" — each a dict
    of assumption key→value pairs that passed validation.
    """
    cache = _load()
    key   = _cache_key(location, facility_type, kw_per_rack)

    cache[key] = {
        "fetched_at":    _now_iso(),
        "location":      location,
        "facility_type": facility_type,
        "kw_per_rack":   round(kw_per_rack, 1),
        "llm_raw":       llm_raw,
        "audit":         audit,
        "overrides":     overrides,
    }

    _save(cache)


def invalidate(location: str, facility_type: str, kw_per_rack: float = 6.0) -> bool:
    """
    Force-expire a specific cache entry.
    Returns True if an entry was removed, False if it did not exist.
    """
    cache = _load()
    key   = _cache_key(location, facility_type, kw_per_rack)

    if key not in cache:
        return False

    del cache[key]
    _save(cache)
    return True


def invalidate_all() -> int:
    """
    Clear the entire cache. Returns number of entries removed.
    """
    cache = _load()
    count = len(cache)
    _save({})
    return count


def status() -> list:
    """
    Return a summary of all cache entries with age and freshness.
    Useful for debugging and the /api/market-cache-status endpoint.
    """
    cache = _load()
    now   = datetime.now(timezone.utc)
    rows  = []

    for key, entry in cache.items():
        try:
            ts  = datetime.fromisoformat(entry["fetched_at"])
            age = now - ts
            age_days = round(age.total_seconds() / 86400, 1)
        except Exception:
            age_days = None

        rows.append({
            "key":           key,
            "location":      entry.get("location"),
            "facility_type": entry.get("facility_type"),
            "fetched_at":    entry.get("fetched_at"),
            "age_days":      age_days,
            "fresh":         _is_fresh(entry),
            "fields_sourced": [
                a["llm_field"]
                for a in entry.get("audit", [])
                if a.get("source") == "llm"
            ],
        })

    return rows


def extract_overrides(entry: dict) -> tuple[dict, dict, dict]:
    """
    Unpack a cache entry's overrides into (rev_overrides, capex_overrides, loan_overrides).
    Returns three empty dicts if overrides are missing.
    """
    overrides = entry.get("overrides", {})
    return (
        deepcopy(overrides.get("revenue", {})),
        deepcopy(overrides.get("capex",   {})),
        deepcopy(overrides.get("loan",    {})),
    )
