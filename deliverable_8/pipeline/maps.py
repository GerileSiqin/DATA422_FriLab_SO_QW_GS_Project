"""Standalone Leaflet map with area price bars and monthly/segment controls."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from .sources import download


def create_map(root, area_monthly, city_monthly, areas, comparison_month, allow_network):
    folder = root / "outputs/maps"
    assets = folder / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    cached_assets = root / "data/cache/map_assets"
    cached_assets.mkdir(parents=True, exist_ok=True)
    for name, url in [("leaflet.js", "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"),
                      ("leaflet.css", "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css")]:
        if not (cached_assets / name).exists():
            if not allow_network:
                raise ValueError("Map assets are missing. Run with --download once")
            download(url, cached_assets / name)
        shutil.copy2(cached_assets / name, assets / name)
    # Area representative points stay within each area, even for coastal shapes.
    projected = areas.to_crs(2193)
    anchors = projected.geometry.representative_point().to_crs(4326)
    geo = json.loads(areas.to_json())
    for i, feature in enumerate(geo["features"]):
        feature["properties"] = {"area_code": str(areas.iloc[i].area_code),
                                  "area_name": areas.iloc[i].area_name,
                                  "longitude": anchors.iloc[i].x, "latitude": anchors.iloc[i].y}
    cols = [c for c in area_monthly.columns if c != "quarter_start"]
    records = json.loads(area_monthly[cols].to_json(orient="records"))
    template = (root / "pipeline/map_template.html").read_text()
    # Avoid an embedded closing script sequence in source-supplied place names.
    template = template.replace("__GEOGRAPHY__", json.dumps(geo).replace("</", "<\\/"))
    template = template.replace("__RECORDS__", json.dumps(records).replace("</", "<\\/"))
    template = template.replace("__CITY_RECORDS__", city_monthly.to_json(orient='records').replace('</','<\\/'))
    template = template.replace("__MONTH__", comparison_month)
    no_prices = area_monthly.groupby('snapshot_month').airbnb_median_nightly_nzd.apply(lambda s:s.notna().sum()==0)
    no_bonds = ~area_monthly.groupby('snapshot_month').bond_row_available.any()
    source_gaps = 'Airbnb prices unavailable: '+(', '.join(no_prices[no_prices].index) or 'none')+'. Same-quarter suburb bond release unavailable: '+(', '.join(no_bonds[no_bonds].index) or 'none')+'.'
    template = template.replace('__SOURCE_GAPS__',source_gaps)
    investigation_path=root/'Raw data/inside_airbnb_christchurch_checks/investigation_manifest.json'
    audit_note=''
    if investigation_path.exists():
        investigation=json.loads(investigation_path.read_text())
        audit_note=(f"Verified source check: {len(investigation['results'])} detailed NZ snapshots matched only to Christchurch City, plus complete Christchurch calendar scans for December–February. "
                    f"Additional recoverable listing prices: {investigation['recoverable_price_count']}. Price gaps in those months remain unavailable. ")
    template=template.replace('__RECOVERY_AUDIT_NOTE__',audit_note)
    (folder / "christchurch_price_bars.html").write_text(template)
    return folder / "christchurch_price_bars.html"
