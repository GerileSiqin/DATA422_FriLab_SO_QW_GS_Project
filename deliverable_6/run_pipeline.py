"""Run the Deliverable 6 pipeline with explicit, portable configuration."""

import argparse
import json
import logging
from pathlib import Path

import pandas as pd

from pipeline.config import Config
from pipeline.geography import enrich_coordinates, load_cache
from pipeline.outputs import write_outputs
from pipeline.transforms import join_bonds, prepare_airbnb, prepare_bonds, rank_gaps, summarise_locations
from pipeline.validation import sanity_check

HERE = Path(__file__).resolve().parent


def parse_config() -> Config:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=HERE / "config.json")
    parser.add_argument("--airbnb", type=Path, default=HERE.parent / "deliverable_3/data_processed/christchurch_airbnb_cleaned.csv")
    parser.add_argument("--bonds", type=Path, default=HERE.parent / "deliverable_4/bond_data_processed/bond_data_clean_qi.csv")
    parser.add_argument("--cache", type=Path, default=HERE / "inputs/koordinates_coordinate_cache.csv")
    parser.add_argument("--output", type=Path, default=HERE / "results")
    parser.add_argument("--workers", type=int)
    parser.add_argument("--minimum-priced-listings", type=int)
    parser.add_argument("--allow-network", action="store_true", help="Query uncached/failed coordinates; requires an environment API key")
    args = parser.parse_args()
    settings = json.loads(args.config.read_text(encoding="utf-8"))
    config = Config(args.airbnb, args.bonds, args.cache, args.output, args.allow_network,
                    args.workers if args.workers is not None else settings["workers"],
                    args.minimum_priced_listings if args.minimum_priced_listings is not None else settings["minimum_priced_listings"])
    config.validate()
    return config


def run_pipeline(config: Config) -> dict:
    """Orchestrate focused stages and publish evidence only after validation."""
    config.validate()
    for folder in (config.output, config.output / "data_processed", config.output / "plots"):
        folder.mkdir(parents=True, exist_ok=True)
    success = config.output / "_SUCCESS.json"
    if success.exists():
        success.unlink()
    airbnb = prepare_airbnb(pd.read_csv(config.airbnb))
    bonds = prepare_bonds(pd.read_csv(config.bonds))
    cache = load_cache(config.cache)
    enriched = enrich_coordinates(airbnb, cache, config.allow_network, config.workers,
                                   config.output / "koordinates_coordinate_cache.csv")
    joined = join_bonds(enriched, bonds)
    summary = summarise_locations(joined)
    ranked = rank_gaps(summary, config.minimum_priced_listings)
    quality = sanity_check(airbnb, joined, summary)
    write_outputs(config, airbnb, enriched, bonds, joined, summary, ranked, quality)
    logging.info("Complete: %s joined rows, %s checks passed", len(joined), len(quality["checks"]))
    return quality


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    try:
        run_pipeline(parse_config())
    except (ValueError, OSError, KeyError, TypeError) as error:
        raise SystemExit(f"Pipeline stopped: {error}") from None


if __name__ == "__main__":
    main()
