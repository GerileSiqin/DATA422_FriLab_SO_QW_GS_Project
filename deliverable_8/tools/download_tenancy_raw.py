"""Save the current Tenancy Services CSV releases in the requested Raw data folder."""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from pipeline.sources import BOND_PAGE, Links, digest, save_json


def main():
    destination = ROOT / "Raw data"
    destination.mkdir(exist_ok=True)
    page = requests.get(BOND_PAGE, timeout=(15, 60))
    page.raise_for_status()
    parser = Links()
    parser.feed(page.text)
    candidates = []
    for label, href in parser.links:
        lowered = label.lower()
        if "by territorial authority" in lowered:
            category = "monthly_territorial_authority"
        elif "by region" in lowered:
            category = "monthly_region"
        elif "detailed quarterly" in lowered and "2020" in lowered:
            category = "quarterly_sa2"
        else:
            continue
        candidates.append((category, label, urljoin(BOND_PAGE, href)))
    if {x[0] for x in candidates} != {"monthly_territorial_authority", "monthly_region", "quarterly_sa2"}:
        raise ValueError("The official page did not expose all three current CSV releases")
    records = []
    for category, label, url in candidates:
        response = requests.get(url, timeout=(15, 90))
        response.raise_for_status()
        content = response.content
        if content.lstrip().lower().startswith((b"<!doctype html", b"<html")):
            raise ValueError(f"Download returned HTML instead of CSV: {category}")
        sha = hashlib.sha256(content).hexdigest()
        filename = Path(unquote(urlparse(url).path)).name
        if not filename.lower().endswith(".csv"):
            filename = category + ".csv"
        path = destination / filename
        # Preserve any existing source revision, including the user-supplied file.
        if path.exists() and digest(path) != sha:
            path = path.with_name(path.stem + "_" + sha[:12] + path.suffix)
        if not path.exists():
            temporary = path.with_suffix(path.suffix + ".tmp")
            temporary.write_bytes(content)
            temporary.replace(path)
        if digest(path) != sha:
            raise ValueError(f"Saved download hash mismatch: {path.name}")
        try:
            frame = pd.read_csv(path, dtype="string", encoding="utf-8-sig", na_values=["NULL"])
            encoding = "utf-8-sig"
        except UnicodeDecodeError:
            frame = pd.read_csv(path, dtype="string", encoding="cp1252", na_values=["NULL"])
            encoding = "cp1252"
        date_field = next((c for c in ("TimeFrame", "Time Frame") if c in frame), None)
        if date_field is None or frame.empty:
            raise ValueError(f"Unexpected or empty CSV schema: {path.name}")
        dates = pd.to_datetime(frame[date_field], errors="coerce")
        if dates.isna().any():
            raise ValueError(f"Unparseable TimeFrame values: {path.name}")
        periods = sorted(dates.dt.strftime("%Y-%m-%d").unique().tolist())
        entry = {"category": category, "path": str(path.relative_to(ROOT)),
                 "publisher_label": label, "url": url, "sha256": sha,
                 "bytes": path.stat().st_size, "rows": len(frame),
                 "columns": frame.columns.tolist(), "encoding": encoding, "date_field": date_field,
                 "first_timeframe": periods[0], "last_timeframe": periods[-1],
                 "requested_late_periods_present": [p for p in periods if "2026-07-01" <= p <= "2026-08-31"]}
        if category == "monthly_territorial_authority" and "Location Id" in frame:
            city = frame.loc[frame["Location Id"].str.strip().str.zfill(3).eq("060")]
            entry["christchurch_rows"] = len(city)
            entry["christchurch_last_timeframe"] = city[date_field].max() if len(city) else None
        records.append(entry)
        print(json.dumps({k: entry[k] for k in ["category", "path", "rows", "first_timeframe", "last_timeframe"]}), flush=True)
    quarterly = next(r for r in records if r["category"] == "quarterly_sa2")
    report = {"downloaded_at_utc": datetime.now(timezone.utc).isoformat(), "source_page": BOND_PAGE,
              "files": records,
              "july_september_2026_sa2_quarter_available": quarterly["last_timeframe"] >= "2026-07-01",
              "note": "Monthly territorial-authority and regional series have coarser geography than the detailed SA2 series. They cannot fill suburb-level gaps without changing the comparison's geographic level."}
    save_json(destination / "tenancy_download_manifest.json", report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
