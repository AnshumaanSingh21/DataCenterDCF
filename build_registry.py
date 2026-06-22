"""
Registry builder — run this manually to populate / refresh outputs/registry_cache.json.

Extraction tiers (per assumption, per market):
  1. RAG  — similarity search over local knowledge base → Gemini extraction
  2. LLM  — ask Gemini directly from world knowledge (no retrieved context)

Values are cached with per-assumption TTLs defined in market_registry.py.
A cached entry is skipped if last_updated + expires_days > today.
Re-run any time; only stale or missing entries are refreshed.
"""

import sys
import os
import json
from datetime import date, datetime

sys.path.insert(0, os.path.dirname(__file__))

from src.agents.market_agent import market_agent
from src.registry.market_registry import MARKET_ASSUMPTIONS, ASSUMPTION_TTL
from src.extraction.assumption_schema import ASSUMPTION_DEFINITIONS
from src.llm.llm_interface import extract_with_llm

CACHE_PATH = os.path.join("outputs", "registry_cache.json")

MARKETS = [
    ("Mumbai",    "retail_colo"),
    ("Mumbai",    "wholesale"),
    ("Hyderabad", "retail_colo"),
    ("Hyderabad", "wholesale"),
    ("Bangalore", "retail_colo"),
    ("Bangalore", "wholesale"),
    ("Delhi",     "retail_colo"),
    ("Delhi",     "wholesale"),
    ("Chennai",   "retail_colo"),
    ("Pune",      "retail_colo"),
]

CONFIDENCE_THRESHOLD = 0.5


# ── Cache helpers ─────────────────────────────────────────────────────────────

def load_cache():
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_cache(cache):
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)


def is_fresh(entry):
    """Return True if the cached entry has not yet expired."""
    try:
        last = datetime.strptime(entry["last_updated"], "%Y-%m-%d").date()
        ttl  = entry.get("expires_days", 90)
        return (date.today() - last).days < ttl
    except Exception:
        return False


# ── Tier 2: LLM world-knowledge fallback ─────────────────────────────────────

def _llm_world_knowledge(assumption_name, location, facility_type):
    defn = ASSUMPTION_DEFINITIONS[assumption_name]
    prompt = f"""You are a financial data expert on Indian data center markets.

Provide your best estimate for the following assumption.

Location      : {location}
Facility type : {facility_type}
Assumption    : {assumption_name}
Description   : {defn['description']}
Unit          : {defn['unit']}
Valid range   : {defn['valid_range'][0]} to {defn['valid_range'][1]}

Rules:
- Return ONLY valid JSON, no markdown.
- Use your training knowledge of Indian data center industry benchmarks.
- Confidence should reflect how certain you are (0.0–1.0).
- If genuinely uncertain, return a mid-range estimate with low confidence.

Format:
{{
  "value": <number>,
  "confidence": <0.0_to_1.0>,
  "reasoning": "<one line>"
}}"""

    try:
        result = extract_with_llm(prompt)
        value      = result.get("value")
        confidence = result.get("confidence", 0.0)
        reasoning  = result.get("reasoning", "")
        lo, hi = defn["valid_range"]
        if value is not None and lo <= float(value) <= hi:
            return value, confidence, reasoning, "llm_world_knowledge"
    except Exception:
        pass
    return None, 0.0, "LLM world-knowledge fallback failed", "llm_world_knowledge"


# ── Main builder ─────────────────────────────────────────────────────────────

def build(force=False):
    cache = load_cache()
    today = date.today().isoformat()

    for location, facility_type in MARKETS:
        market_key = f"{location}|{facility_type}"
        print(f"\n{'='*60}")
        print(f"  {location} / {facility_type}")
        print(f"{'='*60}")

        cache.setdefault(location, {}).setdefault(facility_type, {})
        market_cache = cache[location][facility_type]

        # Which assumptions need refreshing?
        stale = [
            name for name in MARKET_ASSUMPTIONS
            if force
            or name not in market_cache
            or not is_fresh(market_cache[name])
        ]

        if not stale:
            print("  All assumptions fresh — skipping.")
            continue

        print(f"  Stale / missing: {stale}")

        # ── Tier 1: RAG extraction ────────────────────────────────────────────
        print("  [Tier 1] Running RAG extraction...")
        try:
            rag_results = market_agent(location, facility_type)
        except Exception as e:
            print(f"  [Tier 1] RAG failed: {e}")
            rag_results = {}

        for name in stale:
            ttl = ASSUMPTION_TTL.get(name, 90)
            rag = rag_results.get(name, {})
            value      = rag.get("value")
            confidence = rag.get("confidence", 0.0)
            reasoning  = rag.get("reasoning", "")
            source     = "rag"

            if value is not None and confidence >= CONFIDENCE_THRESHOLD:
                print(f"  [RAG  ] {name}: {value}  (conf={confidence:.2f})")
            else:
                # ── Tier 2: LLM world knowledge ───────────────────────────────
                print(f"  [Tier 2] RAG insufficient for {name} — trying LLM world knowledge...")
                value, confidence, reasoning, source = _llm_world_knowledge(
                    name, location, facility_type
                )
                if value is not None:
                    print(f"  [LLM  ] {name}: {value}  (conf={confidence:.2f})")
                else:
                    print(f"  [MISS ] {name}: no value found — keeping previous or skipping")
                    if name in market_cache:
                        continue  # keep the existing cached value

            if value is not None:
                market_cache[name] = {
                    "value":        value,
                    "confidence":   round(confidence, 3),
                    "reasoning":    reasoning,
                    "source":       source,
                    "last_updated": today,
                    "expires_days": ttl,
                }

        save_cache(cache)
        print(f"  Cache saved -> {CACHE_PATH}")

    print(f"\nDone. Registry cache: {CACHE_PATH}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Build market assumption registry cache")
    parser.add_argument("--force", action="store_true", help="Ignore TTL and re-extract everything")
    args = parser.parse_args()
    build(force=args.force)
