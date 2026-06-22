"""
Web loader — fetches URLs from knowledge_base/web_sources.json via Jina Reader
and saves clean text to knowledge_base/web_content/.

Usage:
    cd src/rag
    python web_loader.py           # fetch only new / missing URLs
    python web_loader.py --force   # re-fetch everything

After running, rebuild the FAISS index:
    python build_knowledge_base.py
"""

import sys
import os
import json
import re
import argparse
import time
from pathlib import Path

import urllib.request
import urllib.error

PROJECT_ROOT  = Path(__file__).resolve().parents[2]
SOURCES_FILE  = PROJECT_ROOT / "knowledge_base" / "web_sources.json"
OUTPUT_DIR    = PROJECT_ROOT / "knowledge_base" / "web_content"
JINA_PREFIX   = "https://r.jina.ai/"


def _slug(url: str, description: str) -> str:
    """Turn a URL + description into a safe filename."""
    base = description if description else url
    base = re.sub(r"[^\w\s-]", "", base.lower())
    base = re.sub(r"[\s]+", "_", base.strip())
    return base[:80] + ".txt"


def fetch_url(url: str) -> str:
    jina_url = JINA_PREFIX + url
    req = urllib.request.Request(
        jina_url,
        headers={"User-Agent": "Mozilla/5.0", "Accept": "text/plain"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")


def load_sources() -> list:
    if not SOURCES_FILE.exists():
        print(f"ERROR: {SOURCES_FILE} not found.")
        return []
    with open(SOURCES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [s for s in data.get("sources", []) if "url" in s]


def run(force: bool = False):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    sources = load_sources()

    if not sources:
        print("No sources found in web_sources.json.")
        return

    print(f"Found {len(sources)} source(s).")
    fetched = skipped = failed = 0

    for i, source in enumerate(sources, 1):
        url         = source["url"]
        description = source.get("description", "")
        category    = source.get("category", "general")
        filename    = _slug(url, description)
        out_path    = OUTPUT_DIR / filename

        if out_path.exists() and not force:
            print(f"[{i}/{len(sources)}] SKIP (exists)  {description or url}")
            skipped += 1
            continue

        print(f"[{i}/{len(sources)}] Fetching  {description or url}")
        try:
            text = fetch_url(url)
            # Prepend metadata header so the retriever knows the source
            header = (
                f"SOURCE: {url}\n"
                f"CATEGORY: {category}\n"
                f"DESCRIPTION: {description}\n"
                f"{'='*60}\n\n"
            )
            out_path.write_text(header + text, encoding="utf-8")
            print(f"           Saved -> {filename}")
            fetched += 1
            time.sleep(1)  # be polite to Jina
        except Exception as e:
            print(f"           FAILED: {e}")
            failed += 1

    print(f"\nDone.  Fetched: {fetched}  Skipped: {skipped}  Failed: {failed}")
    print(f"Text files -> {OUTPUT_DIR}")
    if fetched:
        print("\nNext step: rebuild the FAISS index")
        print("  cd src/rag")
        print("  python build_knowledge_base.py")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true",
                        help="Re-fetch all URLs even if already saved")
    args = parser.parse_args()
    run(force=args.force)
