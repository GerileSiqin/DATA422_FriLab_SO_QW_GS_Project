"""Download versioned public inputs and record their exact provenance."""
from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin

import pandas as pd
import requests

LOG = logging.getLogger(__name__)
AIRBNB_PAGE = "https://insideairbnb.com/get-the-data/"
BOND_PAGE = "https://www.tenancy.govt.nz/about-tenancy-services/data-and-statistics/rental-bond-data/"


def input_sources(manifest):
    return manifest['airbnb']+[manifest['bonds']]+([manifest['city_monthly_bonds']] if 'city_monthly_bonds' in manifest else [])+manifest.get('airbnb_price_investigation_sources',[])


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def save_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n")
    temporary.replace(path)


def get(url: str, **kwargs):
    """Public requests only. Credential-bearing requests live in geography.py."""
    response = requests.get(url, timeout=(15, 90), **kwargs)
    response.raise_for_status()
    return response


def download(url: str, destination: Path) -> dict:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not destination.exists():
        LOG.info("Downloading %s", destination.name)
        response = get(url)
        temporary = destination.with_suffix(destination.suffix + ".tmp")
        temporary.write_bytes(response.content)
        temporary.replace(destination)
    return {"path": str(destination), "url": url, "sha256": digest(destination),
            "bytes": destination.stat().st_size}


def walk(value):
    if isinstance(value, dict):
        yield value
        for item in value.values():
            yield from walk(item)
    elif isinstance(value, list):
        for item in value:
            yield from walk(item)


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.href = None
        self.label = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.href = dict(attrs).get("href")
            self.label = []

    def handle_data(self, data):
        if self.href:
            self.label.append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self.href:
            self.links.append(("".join(self.label).strip(), self.href))
            self.href = None


def prepare_inputs(root: Path, config: dict, allow_download: bool) -> dict:
    manifest_path = root / "data/raw/source_manifest.json"
    if not allow_download:
        if not manifest_path.exists():
            raise ValueError("No source manifest. Run with --download first.")
        manifest = json.loads(manifest_path.read_text())
        if manifest['scope'] != {'start_month':config['start_month'],'end_month':config['end_month']}:
            raise ValueError('Configured scope changed; run with --download to refresh the source manifest')
        for item in input_sources(manifest):
            p = root / item["path"]
            if not p.is_file() or digest(p) != item["sha256"]:
                raise ValueError(f"Missing or changed source: {item['path']}")
        return manifest

    # Gatsby's own page metadata exposes the historical snapshot catalogue.
    page = get("https://insideairbnb.com/page-data/get-the-data/page-data.json").json()
    snapshots = []
    for query_hash in page["staticQueryHashes"]:
        url = f"https://insideairbnb.com/page-data/sq/d/{query_hash}.json"
        payload = get(url).json()
        candidates = [v for v in walk(payload) if v.get("link") == "new-zealand"
                      and v.get("publishDate") and v.get("visualisationPublishStatus")]
        if candidates:
            snapshots.extend(candidates)
            save_json(root / "data/raw/airbnb/publisher_snapshot_index.json", payload)
    by_month = {}
    # Older monthly snapshots can remain publicly available after leaving the
    # publisher's rolling index. Dates here must be verified against live URLs.
    for date in config.get("additional_archive_dates", []):
        snapshots.append({"publishDate": date, "dataRoot": "https://data.insideairbnb.com/new-zealand/",
                          "scrapeID": None})
    for entry in snapshots:
        month = entry["publishDate"][:7]
        if config["start_month"] <= month <= config["end_month"]:
            if month not in by_month or entry["publishDate"] > by_month[month]["publishDate"]:
                by_month[month] = entry
    if not by_month:
        raise ValueError("The publisher index contains no requested NZ snapshots")
    records = []
    for month, entry in sorted(by_month.items()):
        date = entry["publishDate"]
        url = entry["dataRoot"] + date + "/visualisations/listings.csv"
        item = download(url, root / f"data/raw/airbnb/{date}_listings.csv")
        item.update(path=str(Path(item["path"]).relative_to(root)), snapshot_date=date,
                    snapshot_month=month, source="Inside Airbnb", publisher_scrape_id=entry["scrapeID"])
        records.append(item)
    parser = Links()
    parser.feed(get(BOND_PAGE).text)
    quarterly = [(label, href) for label, href in parser.links
                 if "detailed quarterly" in label.lower() and "2020" in label]
    if not quarterly:
        raise ValueError("Cannot find the official detailed quarterly bond download")
    label, href = quarterly[0]
    # The publisher can revise the file at the same URL. Preserve every distinct
    # downloaded revision under its content hash instead of overwriting inputs.
    bond_url = urljoin(BOND_PAGE, href)
    bond_response = get(bond_url)
    bond_hash = hashlib.sha256(bond_response.content).hexdigest()
    bond_path = root / f'data/raw/tenancy/quarterly_{bond_hash[:16]}.csv'
    if not bond_path.exists():
        bond_path.write_bytes(bond_response.content)
    bond = {'path':str(bond_path),'url':bond_url,'sha256':bond_hash,'bytes':bond_path.stat().st_size}
    bond.update(path=str(Path(bond["path"]).relative_to(root)), source="MBIE Tenancy Services",
                publisher_label=label, source_page=BOND_PAGE)
    expected = [str(p) for p in pd.period_range(config["start_month"], config["end_month"], freq="M")]
    manifest = {"retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
                "scope": {"start_month": config["start_month"], "end_month": config["end_month"]},
                "airbnb": records, "bonds": bond,
                "missing_airbnb_months": sorted(set(expected) - set(by_month)),
                "source_pages": [AIRBNB_PAGE, BOND_PAGE]}
    save_json(manifest_path, manifest)
    return manifest
