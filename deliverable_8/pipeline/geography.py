"""Use Koordinates APIs for a vintage-compatible city geography and QA probes.

Download each polygon once, then perform all point-in-polygon assignments
locally. This avoids tens of thousands of redundant coordinate API requests.
"""
from __future__ import annotations

import json
import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import geopandas as gpd
import pandas as pd
import requests
from dotenv import load_dotenv

from .sources import digest, save_json, get

LOG = logging.getLogger(__name__)
API = "https://koordinates.com/services/query/v1/vector.json"


def api_request(url: str, key: str, params: dict) -> dict:
    """Use header auth; never expose URLs containing credentials or response bodies."""
    for attempt in range(5):
        try:
            response = requests.get(url, params=params, headers={"Authorization": "key " + key},
                                    timeout=(15, 90))
        except requests.RequestException:
            if attempt == 4:
                raise RuntimeError("Koordinates connection failed after 5 attempts") from None
            time.sleep(2 ** attempt)
            continue
        if response.status_code == 200:
            try:
                return response.json()
            except ValueError:
                raise RuntimeError("Koordinates returned invalid JSON") from None
        if response.status_code not in (429, 500, 502, 503, 504) or attempt == 4:
            raise RuntimeError(f"Koordinates HTTP {response.status_code}; check API key and permissions")
        retry_after = response.headers.get("Retry-After", "")
        time.sleep(min(60, int(retry_after)) if retry_after.isdigit() else 2 ** attempt)
    raise RuntimeError("Koordinates request failed")


def point_features(longitude: float, latitude: float, key: str, layer: int) -> list:
    payload = api_request(API, key, {"layer": layer, "x": longitude, "y": latitude,
                                   "radius": 0, "max_results": 5, "geometry": "false"})
    try:
        return payload["vectorQuery"]["layers"][str(layer)]["features"]
    except (KeyError, TypeError):
        raise RuntimeError("Unexpected Koordinates point-query schema") from None


def get_city_polygons(root: Path, config: dict, allow_network: bool) -> gpd.GeoDataFrame:
    path = root / "data/cache/christchurch_sa2_2019.geojson"
    metadata_path = root / "data/cache/geography_provenance.json"
    if path.exists() and metadata_path.exists():
        provenance = json.loads(metadata_path.read_text())
        if provenance["sha256"] != digest(path):
            raise ValueError("Geographic cache hash mismatch")
        return gpd.read_file(path)
    if not allow_network:
        raise ValueError("No geographic cache. First run requires --download and a Koordinates API key")
    load_dotenv(root / ".env", override=False)
    key = os.getenv("KOORDINATES_API_KEY", "")
    if not key or key == "PASTE_YOUR_KEY_HERE":
        raise ValueError("Save KOORDINATES_API_KEY in the local .env file first")
    probe = point_features(172.6362, -43.5321, key, config["sa2_layer_id"])
    if len(probe) != 1 or probe[0]["properties"].get(config["sa2_code_field"]) != "326600":
        raise ValueError("Single-query test did not identify Christchurch Central SA2 326600")
    LOG.info("Koordinates single-query test passed: Christchurch Central (326600)")
    layer = config["city_geography_layer_id"]
    metadata_url = f"https://datafinder.stats.govt.nz/services/api/v1/layers/{layer}/"
    # Public catalogue metadata does not require a token. Some restricted query
    # keys are rejected by the separate administrative API when sent here.
    metadata = get(metadata_url).json()
    save_json(root / f"data/cache/layer_{layer}_metadata.json", metadata)
    features = []
    start = 0
    endpoint = f"https://services.koordinates.com/featuredata/layer/{layer}/"
    while True:
        payload = api_request(endpoint, key, {"query": json.dumps({"TA2019_V1_00": "060"}),
                                             "start": start, "count": 1000,
                                             "sort": "__pk__", "include_geom": "true"})
        items = payload.get("items")
        if not isinstance(items, list):
            raise ValueError("Unexpected Koordinates Feature Data schema")
        for item in items:
            if item.get("TA2019_V1_00") != "060":
                raise ValueError("Koordinates returned a non-Christchurch feature")
            geom = item.get("__geometry__")
            if geom:
                props = {k: v for k, v in item.items() if not k.startswith("__")}
                features.append({"type": "Feature", "properties": props, "geometry": geom})
        start += len(items)
        if not items or start >= payload["numRows"]:
            break
    if not features:
        raise ValueError("No Christchurch polygons returned")
    areas = gpd.GeoDataFrame.from_features(features, crs="EPSG:4326")
    areas = areas.rename(columns={config["sa2_code_field"]: "area_code",
                                  config["sa2_name_field"]: "area_name"})
    areas["area_code"] = areas["area_code"].astype("string")
    if areas["area_code"].duplicated().any() or not areas.geometry.is_valid.all():
        raise ValueError("City polygons have duplicate area codes or invalid geometry")
    areas.to_file(path, driver="GeoJSON")
    save_json(metadata_path, {"retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
                             "source": endpoint, "metadata_url": metadata_url,
                             "point_query_layer_id": config["sa2_layer_id"],
                             "polygon_layer_id": layer, "vintage": "2019",
                             "territorial_authority_code": "060", "crs": "EPSG:4326",
                             "polygon_count": len(areas), "sha256": digest(path),
                             "probe_area_code": "326600"})
    LOG.info("Cached %s Christchurch SA2 2019 polygons", len(areas))
    return areas


def assign_areas(frame: pd.DataFrame, areas: gpd.GeoDataFrame, root: Path,
                 config: dict, allow_network: bool) -> tuple[pd.DataFrame, dict]:
    coordinates = frame[["longitude", "latitude"]].drop_duplicates().reset_index(drop=True)
    points = gpd.GeoDataFrame(coordinates, geometry=gpd.points_from_xy(
        coordinates.longitude, coordinates.latitude), crs="EPSG:4326")
    assigned = gpd.sjoin(points, areas[["area_code", "area_name", "geometry"]],
                         how="left", predicate="within")
    if assigned.index.duplicated().any():
        raise ValueError("Overlapping polygons produced multiple SA2 assignments")
    # Do not assign an arbitrary nearest polygon to a coastal/boundary point.
    assigned["geography_status"] = assigned["area_code"].notna().map(
        {True: "within_polygon", False: "outside_or_on_boundary"})
    projected_areas = areas.to_crs(2193).set_index("area_code")
    projected_points = points.to_crs(2193)
    distances = []
    for idx, row in assigned.iterrows():
        distances.append(projected_points.loc[idx, "geometry"].distance(
            projected_areas.loc[row["area_code"], "geometry"].boundary)
            if pd.notna(row["area_code"]) else float("nan"))
    assigned["distance_to_sa2_boundary_m"] = distances
    assigned["near_sa2_boundary"] = assigned.distance_to_sa2_boundary_m.le(config["boundary_warning_metres"])
    sample_path = root / "data/cache/point_query_validation.csv"
    if allow_network:
        load_dotenv(root / ".env", override=False)
        key = os.getenv("KOORDINATES_API_KEY", "")
        if key and key != "PASTE_YOUR_KEY_HERE":
            matched = assigned[assigned.area_code.notna()]
            # A deterministic spread across suburbs, plus boundary-adjacent cases.
            sample = pd.concat([matched.groupby("area_code", observed=True).head(1).sample(
                min(20, matched.area_code.nunique()), random_state=422),
                matched.nsmallest(5, "distance_to_sa2_boundary_m")]).drop_duplicates(["longitude", "latitude"])
            checks = []
            for row in sample.itertuples():
                result = point_features(row.longitude, row.latitude, key, config["sa2_layer_id"])
                api_codes = sorted(f["properties"][config["sa2_code_field"]] for f in result)
                checks.append({"longitude": row.longitude, "latitude": row.latitude,
                               "local_area_code": row.area_code, "api_area_codes": ";".join(api_codes),
                               "agrees": row.area_code in api_codes})
            pd.DataFrame(checks).to_csv(sample_path, index=False)
            if checks and not all(c["agrees"] for c in checks):
                raise ValueError("Koordinates point API and local polygon assignments disagree")
            LOG.info("Independent Koordinates point checks passed: %s", len(checks))
    cache = pd.DataFrame(assigned.drop(columns=["geometry", "index_right"]))
    cache.to_csv(root / "data/cache/coordinate_assignments.csv", index=False)
    merged = frame.merge(cache, on=["longitude", "latitude"], how="left", validate="many_to_one")
    qa = {"unique_coordinates": len(coordinates), "coordinates_assigned": int(cache.area_code.notna().sum()),
          "coordinates_unassigned": int(cache.area_code.isna().sum()),
          "coordinate_boundary_flags": int(cache.near_sa2_boundary.sum()),
          "point_api_validation_available": sample_path.exists()}
    return merged, qa
