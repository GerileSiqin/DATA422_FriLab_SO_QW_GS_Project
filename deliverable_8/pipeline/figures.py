"""Readable scientific figures, with common units and explicit sample sizes."""
from __future__ import annotations

import os
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import box

BLUE = "#24658A"
GOLD = "#C88329"
GREY = "#65727C"


def create_figures(root, joined, area_monthly, city_monthly, areas, config):
    os.environ.setdefault("MPLCONFIGDIR", str(root / "data/cache/matplotlib"))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import TwoSlopeNorm
    from matplotlib.patches import Patch

    folder = root / "outputs/figures"
    folder.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11,
                         "axes.titlesize": 15, "axes.labelsize": 11, "axes.spines.top": False,
                         "axes.spines.right": False, "figure.facecolor": "white", "savefig.facecolor": "white"})
    files = []

    def save(fig, name):
        fig.savefig(folder / f"{name}.png", dpi=190, bbox_inches="tight")
        fig.savefig(folder / f"{name}.pdf", bbox_inches="tight")
        plt.close(fig)
        files.append(str(folder / f"{name}.png"))

    months = sorted(city_monthly.snapshot_month.unique())
    x = np.arange(len(months))
    primary = city_monthly.loc[city_monthly.segment.eq("entire_short_stay")].set_index("snapshot_month").loc[months]
    all_rooms = city_monthly.loc[city_monthly.segment.eq("all_rooms")].set_index("snapshot_month").loc[months]
    availability = city_monthly.loc[city_monthly.segment.eq("entire_short_stay_with_availability")].set_index("snapshot_month").loc[months]
    fig, ax = plt.subplots(figsize=(12, 5.5), layout="constrained")
    ax.plot(x, primary.airbnb_median_nightly_nzd, color=BLUE, marker="o", label="Airbnb entire homes, minimum stay ≤30 nights")
    ax.plot(x, all_rooms.airbnb_median_nightly_nzd, color=GREY, linestyle=":", marker="s", label="Airbnb all room types")
    ax.plot(x, primary.city_bond_nightly_equivalent_nzd, color=GOLD, linestyle="--", marker="D",
            label="Official Christchurch City monthly bond median ÷7")
    missing_positions=np.flatnonzero(primary.airbnb_median_nightly_nzd.isna() & primary.listing_count.gt(0))
    for position in missing_positions:
        ax.axvspan(position-.48,position+.48,color='#EDF0F2',zorder=0)
    if len(missing_positions):
        ax.text(float(np.mean(missing_positions)),.56,'Airbnb price fields empty\nin published source files',transform=ax.get_xaxis_transform(),ha='center',va='center',color=GREY,fontsize=10)
    ax.set(xticks=x, xticklabels=[pd.Period(m).strftime("%b %y") for m in months],
           ylabel="NZD per night", title="Christchurch rental price benchmarks by snapshot", ylim=(0, None))
    ax.grid(axis="y", alpha=.2)
    ax.legend(loc="upper left", fontsize=9)
    fig.text(.01, -.04, "Bond series: official monthly TA 060 median. Suburb-quarter rents remain unavailable in July/August.\nAirbnb asking prices exclude occupancy, operating costs and booking fees; this is not an investment return.", fontsize=9, color=GREY)
    save(fig, "01_monthly_price_benchmarks")

    fig, ax = plt.subplots(figsize=(12, 5.4), layout="constrained")
    ax.plot(x, all_rooms.listing_count, color=GREY, marker="o", label="All Airbnb listings")
    ax.plot(x, primary.listing_count, color=BLUE, marker="s", label="Entire homes, minimum stay ≤30 nights")
    ax.plot(x, availability.listing_count, color=GOLD, marker="^", linestyle="--", label="Entire short stays with availability >0")
    ax.set(xticks=x, xticklabels=[pd.Period(m).strftime("%b %y") for m in months], ylabel="Distinct listings in snapshot",
           title="Christchurch Airbnb listing counts", ylim=(0, None))
    ax.legend(fontsize=9)
    ax.grid(axis="y", alpha=.2)
    fig.text(.01, -.025, "Counts are snapshots. Repeat listings across months are not additional properties; zero availability can mean booked or blocked.", fontsize=9, color=GREY)
    save(fig, "02_monthly_listing_counts")

    rankable = area_monthly.loc[area_monthly.segment.eq("entire_short_stay") & area_monthly.eligible_gap_ranking]
    month = rankable.snapshot_month.max() if len(rankable) else months[-1]
    latest = rankable.loc[rankable.snapshot_month.eq(month)].copy()
    top = latest.nlargest(15, "median_nightly_gap_nzd").sort_values("median_nightly_gap_nzd")
    fig, ax = plt.subplots(figsize=(12, 8), layout="constrained")
    labels = [f"{r.area_name} (n={int(r.usable_gap_count)})" for r in top.itertuples()]
    ax.barh(labels, top.median_nightly_gap_nzd, color=BLUE)
    ax.set(xlabel="Median Airbnb nightly price minus area median weekly bond rent ÷7 (NZD)",
           title=f"Largest observed area price gaps — {month}")
    ax.axvline(0, color=GREY, linewidth=1)
    ax.grid(axis="x", alpha=.2)
    fig.text(.01, -.035, f"Entire homes with minimum stay ≤30 nights; at least {config['minimum_priced_listings']} observed matched prices per area.\nDescriptive asking-price comparison; properties are not matched on bedrooms or quality.", fontsize=9, color=GREY)
    save(fig, "03_largest_area_price_gaps")

    top_prices = latest.nlargest(15, "airbnb_median_nightly_nzd").sort_values("airbnb_median_nightly_nzd")
    y = np.arange(len(top_prices))
    fig, ax = plt.subplots(figsize=(12, 8), layout="constrained")
    ax.barh(y + .18, top_prices.airbnb_median_nightly_nzd, height=.34, color=BLUE, label="Airbnb entire short stays")
    ax.barh(y - .18, top_prices.bond_nightly_equivalent_nzd, height=.34, color=GOLD, label="Area bond median weekly rent ÷7")
    ax.set(yticks=y, yticklabels=top_prices.area_name, xlabel="NZD per night", title=f"Area price comparison — {month}")
    ax.legend(loc="lower right", fontsize=9)
    ax.grid(axis="x", alpha=.2)
    fig.text(.01, -.025, "Highest Airbnb medians among areas with ≥5 observed matched prices. Both series use the same monetary unit.", fontsize=9, color=GREY)
    save(fig, "04_area_price_comparison")

    fig, ax = plt.subplots(figsize=(12, 5.4), layout="constrained")
    for values, label, color, marker in [(all_rooms.geographic_assignment_rate, "Assigned to SA2 2019", BLUE, "o"),
                                        (all_rooms.bond_row_match_rate, "Matched bond row for same quarter", GOLD, "s"),
                                        (all_rooms.city_bond_nightly_equivalent_nzd.notna().astype(float), "City monthly rent benchmark available", "#348063", "x"),
                                        (1 - all_rooms.airbnb_price_missing_rate, "Airbnb price observed", GREY, "^")]:
        ax.plot(x, values * 100, label=label, color=color, marker=marker)
    ax.set(xticks=x, xticklabels=[pd.Period(m).strftime("%b %y") for m in months],
           ylim=(0, 108), ylabel="Coverage (%)", title="Data coverage by snapshot")
    for position in missing_positions:
        ax.axvspan(position-.48,position+.48,color='#EDF0F2',zorder=0)
    if len(missing_positions):
        ax.text(float(np.mean(missing_positions)),42,'Missing Airbnb source prices\n(summary + detailed + calendar checked)',ha='center',color=GREY,fontsize=9)
    ax.legend(loc="lower left", fontsize=9)
    ax.grid(axis="y", alpha=.2)
    fig.text(.01, -.045, "City monthly availability is a source-level indicator (100% = present), not suburb coverage.\nA matched suburb row can still have suppressed rent. Missing releases mean unavailable rent, not zero rent.", fontsize=9, color=GREY)
    save(fig, "05_data_coverage")

    locations = areas.to_crs(2193).merge(latest[["area_code", "median_nightly_gap_nzd", "airbnb_median_nightly_nzd",
                                               "bond_nightly_equivalent_nzd", "airbnb_priced_count"]], on="area_code", how="left")
    # Keep the whole city including Banks Peninsula; provide an urban detail panel.
    urban_box = gpd.GeoSeries([box(172.43, -43.64, 172.82, -43.39)], crs=4326).to_crs(2193).total_bounds
    fig, axes = plt.subplots(1, 2, figsize=(15, 7), layout="constrained", width_ratios=[1.15, 1])
    vals = locations.median_nightly_gap_nzd.dropna()
    lim = max(1, float(vals.abs().max())) if len(vals) else 1
    for ax, urban in zip(axes, [True, False]):
        locations.plot(ax=ax, column="median_nightly_gap_nzd", cmap="PuOr", vmin=-lim, vmax=lim,
                       edgecolor="#FFFFFF", linewidth=.35, missing_kwds={"color": "#E4E7EA"})
        if urban:
            ax.set_xlim(urban_box[0], urban_box[2]);ax.set_ylim(urban_box[1], urban_box[3])
        ax.set_title("Urban Christchurch" if urban else "Whole Christchurch City including Banks Peninsula", fontsize=12)
        ax.set_axis_off()
    scalar = plt.cm.ScalarMappable(norm=plt.Normalize(-lim, lim), cmap="PuOr")
    fig.colorbar(scalar, ax=axes, shrink=.65, label="Median nightly price gap (NZD)")
    fig.suptitle(f"Airbnb entire short stays versus bond rents by SA2 — {month}", fontsize=16)
    fig.text(.01, -.035, "SA2 2019 boundaries from Stats NZ through Koordinates. Grey: missing comparison or fewer than 5 observed gaps.\nColour values compare area asking prices with weekly bond rent ÷7; they are not rental profit or a causal effect.", fontsize=9, color=GREY)
    save(fig, "06_spatial_price_gaps")

    fig, axes = plt.subplots(1, 2, figsize=(15, 7.5), layout="constrained", width_ratios=[1.15, 1])
    all_latest = area_monthly.loc[area_monthly.segment.eq("entire_short_stay") & area_monthly.snapshot_month.eq(month)]
    bars = areas.to_crs(2193).merge(all_latest, on=["area_code", "area_name"], how="left")
    max_price = max(1, bars.airbnb_median_nightly_nzd.max())
    for ax, urban in zip(axes, [True, False]):
        bars.plot(ax=ax, facecolor="#F4F5F6", edgecolor="#C3CBD1", linewidth=.5)
        if urban:
            ax.set_xlim(urban_box[0], urban_box[2]);ax.set_ylim(urban_box[1], urban_box[3])
        bounds = ax.axis()
        height_scale = (bounds[3] - bounds[2]) * .09 / max_price
        width = (bounds[1] - bounds[0]) * .004
        for row in bars.itertuples():
            if not row.priced_count_meets_threshold:
                continue
            anchor = row.geometry.representative_point()
            if not (bounds[0] <= anchor.x <= bounds[1] and bounds[2] <= anchor.y <= bounds[3]):
                continue
            if pd.notna(row.airbnb_median_nightly_nzd):
                ax.bar(anchor.x - width / 1.5, row.airbnb_median_nightly_nzd * height_scale,
                       bottom=anchor.y, width=width, color=BLUE, zorder=3)
            if pd.notna(row.bond_nightly_equivalent_nzd):
                ax.bar(anchor.x + width / 1.5, row.bond_nightly_equivalent_nzd * height_scale,
                       bottom=anchor.y, width=width, color=GOLD, zorder=3)
        # A price key gives the proportional vertical scale within each panel.
        bx, by = bounds[0] + .04 * (bounds[1]-bounds[0]), bounds[2] + .07 * (bounds[3]-bounds[2])
        ax.plot([bx,bx],[by,by+200*height_scale],color="#263442",linewidth=2)
        ax.text(bx+width*2,by+100*height_scale,"NZ$200/night",fontsize=8,va="center")
        ax.set(xlim=bounds[:2], ylim=bounds[2:])
        ax.set_axis_off()
        ax.set_title("Urban Christchurch" if urban else "Whole Christchurch City", fontsize=12)
    fig.suptitle(f"Rental price bars at area representative points — {month}", fontsize=16)
    fig.legend(handles=[Patch(color=BLUE,label="Airbnb entire short stays"),Patch(color=GOLD,label="Area bond median ÷7")],loc="lower center",bbox_to_anchor=(.5,-.055),ncol=2,frameon=False)
    fig.text(.01,-.12,"Bar height represents NZD per night, not building height. Areas require ≥5 observed Airbnb prices.\nDense central bars overlap at this scale; the interactive map supports zoom and individual area selection.",fontsize=9,color=GREY)
    save(fig, "07_spatial_price_bars")
    stock = area_monthly.loc[area_monthly.segment.eq('all_rooms') & area_monthly.snapshot_month.eq(month)
                            & area_monthly.active_bonds.notna()].nlargest(15,'active_bonds').sort_values('active_bonds')
    fig, ax = plt.subplots(figsize=(12,8), layout='constrained')
    y = np.arange(len(stock))
    ax.barh(y+.18,stock.airbnb_listing_count,height=.34,color=BLUE,label='Airbnb listings in snapshot, all room types')
    ax.barh(y-.18,stock.active_bonds,height=.34,color=GOLD,label='Published active bonds, ALL/ALL')
    ax.set(yticks=y,yticklabels=stock.area_name,xlabel='Published count',title=f'Airbnb listings and active rental bonds — {month}')
    ax.legend(loc='lower right',fontsize=9);ax.grid(axis='x',alpha=.2)
    fig.text(.01,-.04,'Fifteen areas with the largest active-bond counts. Compare market scale rather than advertised vacancies.\nAirbnb listings and active bonds describe different products; quarterly bond counts are not summed across snapshots.',fontsize=9,color=GREY)
    save(fig,'08_airbnb_and_active_bonds')
    late = primary.loc[['2026-07','2026-08']]
    fig, ax = plt.subplots(figsize=(10,6),layout='constrained')
    positions=np.arange(len(late))
    a=ax.bar(positions-.19,late.airbnb_median_nightly_nzd,.36,color=BLUE,label='Airbnb entire homes, minimum stay ≤30 nights')
    b=ax.bar(positions+.19,late.city_bond_nightly_equivalent_nzd,.36,color=GOLD,label='Official city monthly bond median ÷7')
    ax.bar_label(a,labels=[f'NZ${r.airbnb_median_nightly_nzd:.2f}\n(n={int(r.priced_count):,})' for r in late.itertuples()],padding=6,fontsize=10)
    ax.bar_label(b,labels=[f'NZ${v:.2f}' for v in late.city_bond_nightly_equivalent_nzd],padding=6,fontsize=10)
    ax.set(xticks=positions,xticklabels=['July 2026','August 2026'],ylabel='NZD per night',ylim=(0,345),title='Christchurch-wide price comparison — July and August 2026')
    ax.legend(loc='upper right',fontsize=9);ax.grid(axis='y',alpha=.18);ax.set_axisbelow(True)
    for i,r in enumerate(late.itertuples()):
        ax.text(i,300,f'Difference of medians: NZ${r.citywide_difference_of_medians_nzd:.2f}/night',ha='center',fontsize=10)
    fig.text(.01,-.06,'City bond median = NZD 550/week in both months (NZD 78.57/night equivalent). n = observed Airbnb prices.\nNo July/August suburb bond release: area rents and area gaps remain unavailable. Different properties and products; gap is not profit.',fontsize=9,color=GREY)
    save(fig,'09_july_august_citywide_comparison')
    return files, month
