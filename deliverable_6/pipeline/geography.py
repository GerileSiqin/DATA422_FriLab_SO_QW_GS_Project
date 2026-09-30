"""Read a provenance-tracked SA2 cache; optionally query missing or failed pairs."""

import json
import logging
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pandas as pd

from .config import CODE_FIELD, ENDPOINT, LAYER_ID, NAME_FIELD
from .transforms import numeric_column, require_columns

LOG = logging.getLogger(__name__)
CACHE_COLUMNS = ["longitude", "latitude", "area_code", "area_name", "query_status"]


def query_sa2(longitude: float, latitude: float, api_key: str, retries: int = 5) -> dict:
    """Retry transient errors without saving URLs, keys, or server bodies."""
    parameters = dict(key=api_key, layer=LAYER_ID, x=longitude, y=latitude,
                      max_results=1, radius=1, geometry="false", with_field_names="true")
    request = urllib.request.Request(ENDPOINT + "?" + urllib.parse.urlencode(parameters),
                                     headers={"User-Agent": "DATA422-Deliverable6/1.0"})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                payload = json.load(response)
            features = payload["vectorQuery"]["layers"][str(LAYER_ID)]["features"]
            if not features:
                return dict(area_code=None, area_name=None, query_status="no_match")
            props = features[0]["properties"]
            if not props.get(CODE_FIELD) or not props.get(NAME_FIELD):
                return dict(area_code=None, area_name=None, query_status="schema_error")
            return dict(area_code=props[CODE_FIELD], area_name=props[NAME_FIELD], query_status="ok")
        except urllib.error.HTTPError as error:
            status = f"http_{error.code}"
            retryable = error.code in {429, 500, 502, 503, 504}
        except (TimeoutError, urllib.error.URLError):
            status, retryable = "network_error", True
        except (KeyError, TypeError, IndexError, ValueError):
            status, retryable = "schema_error", False
        if not retryable or attempt == retries - 1:
            return dict(area_code=None, area_name=None, query_status=status)
        time.sleep(2 ** attempt)
    return dict(area_code=None, area_name=None, query_status="network_error")


def load_cache(path: Path) -> pd.DataFrame:
    cache = pd.read_csv(path, dtype={"area_code": "string"})
    require_columns(cache, set(CACHE_COLUMNS), "SA2 cache")
    cache = cache[CACHE_COLUMNS].copy()
    for column in ("longitude", "latitude"):
        cache[column] = numeric_column(cache, column)
    cache["area_code"] = numeric_column(cache, "area_code", nullable=True, integer=True)
    if cache.duplicated(["longitude", "latitude"]).any():
        raise ValueError("SA2 cache contains duplicate coordinate keys")
    ok = cache["query_status"].eq("ok")
    if (ok & (cache["area_code"].isna() | cache["area_name"].isna() | cache["area_code"].le(0))).any():
        raise ValueError("SA2 cache has incomplete successful responses")
    if (~ok & (cache["area_code"].notna() | cache["area_name"].notna())).any():
        raise ValueError("Unsuccessful cache rows must not contain SA2 values")
    names = cache.loc[ok].groupby("area_code")["area_name"].nunique()
    if names.gt(1).any():
        raise ValueError("SA2 cache assigns inconsistent names to the same code")
    return cache


def enrich_coordinates(airbnb: pd.DataFrame, cache: pd.DataFrame,
                       allow_network: bool, workers: int, cache_output: Path) -> pd.DataFrame:
    """Offline runs require completed pairs; live runs retry failed cache entries."""
    completed = cache["query_status"].isin(["ok", "no_match"])
    reusable = cache.loc[completed].copy()
    keys = set(zip(reusable["longitude"], reusable["latitude"]))
    coordinates = airbnb[["longitude", "latitude"]].drop_duplicates()
    pending = [pair for pair in coordinates.itertuples(index=False, name=None) if pair not in keys]
    LOG.info("Coordinates: %s unique, %s pending", len(coordinates), len(pending))
    if pending and not allow_network:
        raise ValueError(f"Offline cache has {len(pending)} missing or failed pairs; use --allow-network to query them")
    if pending:
        api_key = os.getenv("KOORDINATES_API_KEY")
        if not api_key:
            raise ValueError("Set KOORDINATES_API_KEY for network queries")
        probe = query_sa2(*pending[0], api_key)
        if probe["query_status"] not in {"ok", "no_match"}:
            raise ValueError(f"Single-query test failed: {probe['query_status']}")
        rows = [dict(longitude=pending[0][0], latitude=pending[0][1], **probe)]
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {executor.submit(query_sa2, *pair, api_key): pair for pair in pending[1:]}
            for future in as_completed(futures):
                longitude, latitude = futures[future]
                rows.append(dict(longitude=longitude, latitude=latitude, **future.result()))
                if len(rows) % 100 == 0:
                    write_cache(pd.concat([reusable, pd.DataFrame(rows)], ignore_index=True), cache_output)
        reusable = pd.concat([reusable, pd.DataFrame(rows)], ignore_index=True)
    write_cache(reusable, cache_output)
    reusable = load_cache(cache_output)
    unresolved = reusable["query_status"].isin(["ok", "no_match"])
    if not unresolved.all():
        raise ValueError("SA2 queries failed; inspect output cache and rerun with --allow-network")
    return airbnb.merge(reusable, on=["longitude", "latitude"], how="left",
                        validate="many_to_one", sort=False)


def write_cache(cache: pd.DataFrame, path: Path) -> None:
    """Save checkpoints atomically without modifying the input cache."""
    temporary = path.with_suffix(".csv.tmp")
    cache.to_csv(temporary, index=False)
    temporary.replace(path)
