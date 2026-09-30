"""Write inspectable artifacts and a record of the inputs and software used."""

import hashlib
import json
import platform
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .config import CENTRAL_SA2, LAYER_ID, Config


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def save_plot(summary: pd.DataFrame, ranked: pd.DataFrame, folder: Path) -> None:
    """Keep quarter-specific plots and label missing bond counts explicitly."""
    for quarter, data in summary.groupby("bond_time"):
        stamp = quarter.strftime("%Y-%m-%d")
        top_gaps = ranked.loc[ranked["bond_time"].eq(quarter)].head(15).sort_values("median_nightly_gap")
        fig, ax = plt.subplots(figsize=(11, 7))
        if top_gaps.empty:
            ax.text(0.5, 0.5, "No locations meet the priced-listing minimum", ha="center", transform=ax.transAxes)
        else:
            ax.barh(top_gaps["area_name"].fillna("Unmapped"), top_gaps["median_nightly_gap"], color="#2563A6")
        ax.axvline(0, color="#333333", linewidth=1)
        ax.set_xlabel("Airbnb median nightly price minus weekly bond rent / 7 (NZD)")
        ax.set_title(f"Largest rental price gaps for quarter beginning {stamp}")
        ax.grid(axis="x", alpha=0.2)
        fig.tight_layout()
        fig.savefig(folder / f"01_largest_price_gaps_{stamp}.png", dpi=160)
        plt.close(fig)

        counts = data.nlargest(20, "airbnb_count").sort_values("airbnb_count")
        labels = counts["area_name"].fillna("Unmapped").astype(str)
        labels = labels.where(counts["active_bonds"].notna(), labels + " (bond data missing)")
        y = np.arange(len(counts))
        fig, ax = plt.subplots(figsize=(11, 8))
        ax.barh(y - 0.2, counts["active_bonds"].astype(float), height=0.4, color="#D9A441", label="Active tenancy bonds")
        ax.barh(y + 0.2, counts["airbnb_count"], height=0.4, color="#2563A6", label="Airbnb listings")
        ax.set_yticks(y, labels=labels)
        ax.set_xlabel("Listings and bonds have different source definitions")
        ax.set_title(f"Rental counts for quarter beginning {stamp}")
        ax.legend()
        ax.grid(axis="x", alpha=0.2)
        fig.tight_layout()
        fig.savefig(folder / f"02_property_counts_{stamp}.png", dpi=160)
        plt.close(fig)


def write_outputs(config: Config, airbnb: pd.DataFrame, enriched: pd.DataFrame,
                  bonds: pd.DataFrame, joined: pd.DataFrame, summary: pd.DataFrame,
                  ranked: pd.DataFrame, quality: dict) -> None:
    """Persist tables, regenerate the report, and record completion last."""
    output = config.output
    tables = {"airbnb_prepared": airbnb, "airbnb_enriched": enriched,
              "bond_location_quarter": bonds, "airbnb_bond_joined": joined,
              "location_comparison": summary, "largest_gap_locations": ranked}
    for name, table in tables.items():
        table.to_csv(output / "data_processed" / f"{name}.csv", index=False, date_format="%Y-%m-%d")
    database = output / "deliverable_6.sqlite"
    temporary = output / "deliverable_6.sqlite.tmp"
    if temporary.exists():
        temporary.unlink()
    with sqlite3.connect(temporary) as connection:
        for name, table in tables.items():
            table.to_sql(name, connection, if_exists="replace", index=False)
        persisted = pd.read_sql_query("SELECT COUNT(*) AS n FROM airbnb_bond_joined", connection)["n"].iloc[0]
        if int(persisted) != len(joined):
            raise ValueError("SQLite joined row count differs from dataframe")
    temporary.replace(database)
    quality["checks"]["sqlite_joined_row_count"] = True
    (output / "data_quality_summary.json").write_text(json.dumps(quality, indent=2) + "\n", encoding="utf-8")
    save_plot(summary, ranked, output / "plots")
    paragraphs = ["# Deliverable 6 pipeline results", "",
                  f"Listings retained: {quality['joined_rows']:,}. SA2 matches: {quality['sa2_matches']:,}. "
                  f"Bond rows matched: {quality['bond_row_matches']:,}. Bond rents available: {quality['bond_rent_matches']:,}.",
                  f"Prices missing: {quality['missing_prices']:,}; usable listing price gaps: {quality['usable_price_gaps']:,}.",
                  f"All {len(quality['checks'])} sanity checks passed.", "",
                  "## Results by quarter"]
    for quarter, data in summary.groupby("bond_time"):
        central = data.loc[data["area_code"].eq(CENTRAL_SA2)]
        paragraphs.append(f"\n### Quarter beginning {quarter:%Y-%m-%d}")
        if not central.empty:
            row = central.iloc[0]
            price_text = f"NZ${row['median_airbnb_price']:.2f}" if pd.notna(row['median_airbnb_price']) else "unavailable"
            paragraphs.append(f"Christchurch Central median Airbnb price: {price_text}; "
                              f"{int(row['priced_listing_count'])} priced listings from {int(row['airbnb_count'])} listings.")
        top = ranked.loc[ranked["bond_time"].eq(quarter)].head(1)
        if not top.empty:
            row = top.iloc[0]
            paragraphs.append(f"Largest eligible median gap: {row['area_name']}, NZ${row['median_nightly_gap']:.2f}; "
                              f"{int(row['gap_listing_count'])} usable price gaps from {int(row['airbnb_count'])} listings.")
        else:
            paragraphs.append("No location meets the observed-gap minimum.")
    paragraphs += ["", "## Method and interpretation",
                   f"Use published ALL/ALL bond totals; join by SA2 and quarter using a validated left join. "
                   f"Divide median weekly rent by seven. Rank only locations with at least {config.minimum_priced_listings} observed listing gaps. "
                   "Keep missing prices and unmatched bond values as missing. Count all listings separately from priced listings.",
                   "Active tenancy bonds are a proxy, not a count of unique properties. Airbnb may include private rooms. "
                   "These descriptive price gaps do not measure investment returns or establish a causal effect. "
                   "Different SA2 vintages in the two inputs may explain some unmatched locations; matching codes alone does not resolve this.",
                   "", "## Geographic source",
                   f"SA2 lookup uses the supplied Deliverable 5 cache associated with Koordinates layer {LAYER_ID}. "
                   "Offline reproduction validates cache structure and arithmetic but does not independently verify point-in-polygon assignments or boundary-vintage compatibility."]
    (output / "analysis_summary.md").write_text("\n\n".join(paragraphs) + "\n", encoding="utf-8")
    code_root = Path(__file__).resolve().parents[1]
    pipeline_files = [output / "koordinates_coordinate_cache.csv", database,
                      output / "analysis_summary.md", output / "data_quality_summary.json",
                      *sorted((output / "data_processed").glob("*.csv")),
                      *sorted((output / "plots").glob("*.png"))]
    manifest = dict(created_at_utc=datetime.now(timezone.utc).isoformat(),
                    inputs={name: {"path": str(path.resolve()), "sha256": file_hash(path)}
                            for name, path in (("airbnb", config.airbnb), ("bonds", config.bonds), ("sa2_cache", config.cache))},
                    settings={"allow_network": config.allow_network, "workers": config.workers,
                              "minimum_priced_listings": config.minimum_priced_listings, "sa2_layer_id": LAYER_ID,
                              "days_per_week": 7, "join_keys": ["area_code", "bond_time"]},
                    software={"python": platform.python_version(), "pandas": pd.__version__,
                              "numpy": np.__version__, "matplotlib": matplotlib.__version__},
                    code_sha256={str(p.relative_to(code_root)): file_hash(p)
                                 for p in sorted(code_root.rglob("*.py"))},
                    outputs={str(p.relative_to(output)): file_hash(p) for p in pipeline_files},
                    quality=quality)
    (output / "run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (output / "_SUCCESS.json").write_text(json.dumps({"status": "complete", "checks_passed": len(quality["checks"]),
                                                     "manifest_sha256": file_hash(output / "run_manifest.json")}, indent=2) + "\n", encoding="utf-8")
