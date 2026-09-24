"""Test one Stats NZ SA2 2026 point query before running the batch."""

from __future__ import annotations

import argparse
import json
import os
import urllib.parse
import urllib.request

ENDPOINT = "https://koordinates.com/services/query/v1/vector.json"
LAYER_ID = 123515


def query_point(longitude: float, latitude: float) -> dict[str, str]:
    api_key = os.getenv("KOORDINATES_API_KEY")
    if not api_key:
        raise SystemExit("Set KOORDINATES_API_KEY in the VS Code terminal first.")
    parameters = {
        "key": api_key,
        "layer": LAYER_ID,
        "x": longitude,
        "y": latitude,
        "max_results": 1,
        "radius": 1,
        "geometry": "false",
        "with_field_names": "true",
    }
    request = urllib.request.Request(
        ENDPOINT + "?" + urllib.parse.urlencode(parameters),
        headers={"User-Agent": "DATA422-Airbnb-SA2/1.0"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.load(response)
    features = payload["vectorQuery"]["layers"][str(LAYER_ID)]["features"]
    if not features:
        raise RuntimeError("No SA2 polygon was returned for this point.")
    properties = features[0]["properties"]
    return {
        "area_code": properties["SA22026_V1_00"],
        "area_name": properties["SA22026_V1_00_NAME"],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--longitude", type=float, default=172.65552)
    parser.add_argument("--latitude", type=float, default=-43.50961)
    args = parser.parse_args()
    result = query_point(args.longitude, args.latitude)
    print(f"Layer ID: {LAYER_ID}")
    print(f"SA2 code: {result['area_code']}")
    print(f"SA2 name: {result['area_name']}")

