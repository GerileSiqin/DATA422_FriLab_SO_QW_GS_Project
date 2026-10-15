"""Python-authored analytical and dataset workbooks with native Excel tables."""
from __future__ import annotations

import math
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import xlsxwriter
from .sources import input_sources


DEFINITIONS = {
    'christchurch_listing_count': 'Listings labelled Christchurch City in this exact New Zealand snapshot. Other cities excluded before source comparisons.',
    'summary_observed_prices': 'Positive Christchurch nightly prices in the summary source for the snapshot.',
    'summary_missing_prices': 'Christchurch summary listing records without a valid positive price.',
    'detail_observed_prices': 'Positive same-snapshot prices in the detailed source for the Christchurch listing IDs.',
    'recoverable_detail_prices': 'Missing Christchurch summary prices with a positive price in the exact matching detailed snapshot; zero found in this investigation.',
    'calendar_christchurch_rows': 'All calendar records scanned for the Christchurch listing IDs; calendar dates are future stay dates, not snapshot observation dates.',
    'calendar_observed_prices': 'Christchurch calendar rows with a positive price in fully scanned missing-price snapshots. Blank for snapshots not scanned.',
    'calendar_observed_adjusted_prices': 'Christchurch calendar rows with a positive adjusted_price. Blank for snapshots not scanned.',
    'recovery_status': 'Source investigation outcome for an exact snapshot. No price imputation or cross-city substitution.',
    'summary_rounding_difference_count': 'Observed summary prices rounded to whole NZD compared with detailed prices containing cents. Recorded separately from a quote conflict.',
    "city_bond_weekly_median_nzd": "Official monthly Christchurch City (TA 060) median weekly bond rent; never assigned to individual SA2 areas.",
    "city_bond_nightly_equivalent_nzd": "Official monthly citywide median weekly rent / 7. A comparison unit, not an offered nightly tenancy.",
    "citywide_difference_of_medians_nzd": "Citywide Airbnb median nightly asking price minus official city monthly weekly bond median / 7. Difference of medians, not median matched listing-level gap.",
    "citywide_ratio_of_medians": "Citywide Airbnb median nightly asking price / official city monthly bond nightly equivalent.",
    "city_monthly_bond_row_available": "An exact monthly Christchurch City bond source row exists. No carry-forward.",
    "city_monthly_bond_available": "A valid official Christchurch City monthly median rent exists; does not indicate suburb-quarter availability.",
    "city_active_bonds": "Published monthly Christchurch City active bonds. Stock, not advertised vacancies.",
    "city_bonds_lodged": "Published monthly Christchurch City lodged bonds; a flow, not active stock.",
    "city_closed_bonds": "Published monthly Christchurch City closed bonds.",
    "city_bond_weekly_geomean_nzd": "Published monthly Christchurch City geometric mean weekly rent.",
    "city_bond_weekly_lower_quartile_nzd": "Published monthly Christchurch City lower-quartile weekly rent.",
    "city_bond_weekly_upper_quartile_nzd": "Published monthly Christchurch City upper-quartile weekly rent.",
    "city_code": "Territorial authority code 060 for Christchurch City, stored as text.",
    "city_name": "Official territorial authority name in the monthly tenancy source.",
    "benchmark_geography": "Geographic level of the source benchmark: territorial_authority.",
    "benchmark_frequency": "Source observation frequency: monthly.",
    "listing_id": "Airbnb listing identifier, preserved as text to avoid Excel's 15-digit precision limit.",
    "snapshot_date": "Publisher's date for the source snapshot; not the last-review date.",
    "snapshot_month": "Calendar month of the published snapshot. Each listing occurs at most once per month.",
    "quarter_start": "Calendar quarter start corresponding to the snapshot date or source bond TimeFrame.",
    "area_code": "Stats NZ SA2 2019 code, assigned by point-in-polygon in EPSG:4326.",
    "area_name": "Official SA2 2019 area name.",
    "airbnb_nightly_nzd": "Observed Airbnb nightly asking price in NZD. Missing or nonpositive source prices are missing.",
    "price_raw": "Unmodified price text from the Airbnb source CSV.",
    "bond_weekly_median_nzd": "Published median weekly rent for an SA2-quarter, ALL dwelling types and ALL bedroom counts.",
    "bond_nightly_equivalent_nzd": "Published weekly bond median divided by 7; a comparison unit, not a nightly tenancy offer.",
    "nightly_price_gap_nzd": "Airbnb nightly asking price minus the same-area, same-quarter bond nightly equivalent.",
    "airbnb_to_bond_ratio": "Airbnb nightly asking price divided by the same-area, same-quarter bond nightly equivalent.",
    "active_bonds": "Published count of active bonds. A rental-stock indicator, not advertised vacancies.",
    "bonds_lodged": "Published Total Bonds in a quarter. A flow of bond lodgements, not rental housing stock.",
    "closed_bonds": "Published count of closed bonds for the quarter.",
    "bond_row_matched": "True if an exact SA2-quarter ALL/ALL bond row exists, including rows with missing rents.",
    "comparison_status": "Mutually exclusive reason a row supports, or cannot support, the price-gap comparison.",
    "entire_short_stay": "Entire home/apt with minimum_nights between 1 and 30 inclusive. Main comparison group.",
    "entire_short_stay_with_availability": "Entire short stay with availability_365 >0. Sensitivity group, not a confirmed vacancy.",
    "near_sa2_boundary": "Coordinate lies within 150m of its SA2 boundary. Airbnb may displace coordinates by about 150m.",
    "distance_to_sa2_boundary_m": "Distance from coordinate to assigned SA2 boundary, calculated in NZTM EPSG:2193.",
    "geography_status": "within_polygon or outside_or_on_boundary; no nearest-area imputation is performed.",
    "source_file": "Project-relative path of the immutable source CSV.",
    "source_row": "Original CSV row number including its header, for tracing records to source.",
    "high_price_flag": "Above the snapshot's 99th percentile within room type. Retained in all calculations.",
    "review_after_snapshot": "Last review date is later than the publisher's snapshot date. Flagged for audit.",
    "days_since_last_review": "Publisher snapshot date minus last-review date in days; negative values are flagged.",
    "segment": "Airbnb comparison group; ALL/ALL bond benchmark remains the same across groups.",
    "airbnb_listing_count": "Distinct listings in one SA2 and snapshot month for the selected group. Not additive over months.",
    "airbnb_priced_count": "Listings with an observed positive nightly asking price in this area, month and group.",
    "usable_gap_count": "Listings with an observed Airbnb price and a matching published bond rent.",
    "eligible_gap_ranking": "At least 5 observed matched price gaps in the area, month and comparison group.",
    "priced_count_meets_threshold": "At least 5 observed Airbnb prices in the area, month and comparison group.",
    "airbnb_median_nightly_nzd": "Median of observed positive Airbnb nightly asking prices for this month and group.",
    "median_nightly_gap_nzd": "Median listing-level nightly price gap, within this SA2, month and group.",
    "median_listing_gap_nzd": "Median of matched listing-level gaps across Christchurch; listing weighted, not area weighted.",
    "listing_weighted_area_bond_nightly_median_nzd": "Median of each selected listing's matching area bond rent divided by 7; not a citywide bond median.",
    "snapshot_available": "Whether an in-scope Airbnb snapshot exists. Missing snapshots are not zero counts.",
    "bond_row_available": "Whether the selected area and quarter have a published ALL/ALL bond row.",
    "airbnb_p25_nightly_nzd": "25th percentile of observed Airbnb prices. Distribution spread, not confidence bounds.",
    "airbnb_p75_nightly_nzd": "75th percentile of observed Airbnb prices. Distribution spread, not confidence bounds.",
    "name": "Public listing name in the publisher's summary data.",
    "host_id": "Public host identifier, retained as text.",
    "host_name": "Public host name in the source summary data.",
    "neighbourhood_group": "Publisher's territorial-authority label, used for the initial Christchurch City filter.",
    "neighbourhood": "Publisher's neighbourhood or ward label. Not substituted for an SA2 code.",
    "longitude": "Published approximate longitude in WGS84 decimal degrees, EPSG:4326.",
    "latitude": "Published approximate latitude in WGS84 decimal degrees, EPSG:4326. This is not altitude.",
    "room_type": "Publisher's room-type category. Private/shared/hotel rooms are separated from entire homes.",
    "minimum_nights": "Listing's minimum stay in nights; invalid/nonpositive values become missing.",
    "availability_365": "Days shown available within the next 365 days. Booked and blocked dates cannot be distinguished.",
    "number_of_reviews": "Cumulative review count in the source snapshot.",
    "last_review": "Date of the listing's last published review.",
    "reviews_per_month": "Publisher's average reviews per month.",
    "calculated_host_listings_count": "Publisher's count of listings associated with this host in the data area.",
    "number_of_reviews_ltm": "Publisher's reviews in the last twelve months.",
    "license": "Licence field supplied by the publisher; missing values are retained.",
    "TimeFrame": "Original bond quarter date field.",
    "Location Id": "Original bond location identifier; valid codes are SA2 2019.",
    "dwelling_type": "Published tenancy dwelling category. ALL rows are not summed with their components.",
    "number_of_beds": "Published tenancy bedroom category; ALL is the main all-bedroom benchmark.",
    "bond_weekly_geomean_nzd": "Published geometric mean weekly rent for this bond category.",
    "bond_weekly_lower_quartile_nzd": "Published lower-quartile weekly rent; source methodology may use synthetic quartiles.",
    "bond_weekly_upper_quartile_nzd": "Published upper-quartile weekly rent; source methodology may use synthetic quartiles.",
    "Log Std Dev Weekly Rent": "Published log standard deviation of weekly rent, retained from the tenancy source.",
    "bond_log_std_weekly_rent": "Published log standard deviation of weekly tenancy rent.",
    "bond_join_status": "Pandas join indicator: both indicates an exact ALL/ALL bond match, left_only indicates no match.",
    "price_missing_or_invalid": "True when the source Airbnb price is missing, unparsable or nonpositive.",
    "availability_invalid": "True when source availability is missing or outside 0–365. Flag retained.",
    "minimum_nights_invalid": "True when minimum nights is missing, unparsable or below 1.",
    "median_price_ratio": "Median Airbnb-to-bond nightly equivalent ratio among observed matched listings.",
    "listing_count": "Distinct Airbnb listings in the selected snapshot and comparison group, including those without assigned city SA2.",
    "priced_count": "Selected listings with an observed positive Airbnb asking price.",
    "matched_listing_count": "Selected listings with an exact SA2-quarter bond row, including missing-price listings.",
    "geographic_assignment_rate": "Share of selected listings assigned to an official Christchurch SA2 polygon.",
    "bond_row_match_rate": "Share of selected listings with an exact ALL/ALL SA2-quarter bond row.",
    "airbnb_price_missing_rate": "Share of selected listings with no valid positive Airbnb price.",
    "airbnb_listings_per_active_bond": "Snapshot Airbnb listing count / published active-bond count in the same SA2-quarter. Different market measures; not a vacancy or occupancy rate.",
}


def dictionary(frames):
    fields = sorted(set().union(*(set(f.columns) for f in frames)))
    return pd.DataFrame([{"field": f, "meaning": DEFINITIONS.get(f, "Recorded pipeline quality or source-provenance field; see methodology.")}
                         for f in fields])


def make_workbook(path: Path):
    wb = xlsxwriter.Workbook(str(path), {"strings_to_formulas": False, "strings_to_urls": False,
                                         "nan_inf_to_errors": False})
    wb.set_properties({"title": "Christchurch rental comparison", "author": "DATA422 project",
                       "comments": "Built reproducibly with Python. See Method and sources for definitions."})
    return wb


def table_sheet(wb, name, frame):
    ws = wb.add_worksheet(name)
    ws.hide_gridlines(2)
    ws.freeze_panes(1, 2 if len(frame.columns)>5 else 0)
    ws.set_default_row(18)
    header = wb.add_format({"bold": True,"font_color":"white","bg_color":"#244C68", "font_name":"Arial",
                            "font_size":10,"text_wrap":True,"valign":"vcenter", "align":"center"})
    text = wb.add_format({"font_name":"Arial","font_size":10,"valign":"vcenter"})
    wrapped = wb.add_format({"font_name":"Arial","font_size":10,"valign":"vcenter","text_wrap":True})
    decimal = wb.add_format({"font_name":"Arial","font_size":10,"valign":"vcenter","num_format":"#,##0.00"})
    integer = wb.add_format({"font_name":"Arial","font_size":10,"valign":"vcenter","num_format":"#,##0"})
    percent = wb.add_format({"font_name":"Arial","font_size":10,"valign":"vcenter","num_format":"0.0%"})
    date = wb.add_format({"font_name":"Arial","font_size":10,"num_format":"dd mmm yyyy"})
    identifier = wb.add_format({"font_name":"Arial","font_size":10,"num_format":"@","valign":"vcenter"})
    coordinate = wb.add_format({"font_name":"Arial","font_size":10,"num_format":"0.000000","valign":"vcenter"})
    ws.set_row(0, 48)
    for col, field in enumerate(frame.columns):
        if field in ("meaning", "explanation"):
            width=88
        elif field in ("source_url", "url", "path"):
            width=72
        elif field == "field":
            width=48
        elif field == "topic":
            width=30
        elif field == "sha256":
            width=38
        elif field in ("area_name", "name", "source_file", "definition", "publisher_label"):
            width=36
        elif field in ("listing_id", "host_id"):
            width=23
        else:
            width=min(28,max(17,len(field.replace('_',' '))*.65))
        fmt = percent if field.endswith("_rate") else decimal if ("nzd" in field or "ratio" in field or "log_std" in field or field in ["longitude","latitude","distance_to_sa2_boundary_m"]) else integer if pd.api.types.is_numeric_dtype(frame[field]) else text
        if field in ('meaning','explanation','source_url','url','field','path','sha256'):
            fmt=wrapped
        if field in ('listing_id','host_id','area_code','Location Id','publisher_scrape_id'):
            fmt=identifier
        if field in ('latitude','longitude'):
            fmt=coordinate
        ws.set_column(col,col,width,fmt)
        ws.write(0,col,field.replace("_"," "),header)
    for row_idx, row in enumerate(frame.itertuples(index=False,name=None),1):
        if 'sha256' in frame:
            ws.set_row(row_idx,34)
        if 'meaning' in frame or 'explanation' in frame:
            lines=max([math.ceil(len(str(value))/80) for col,value in enumerate(row)
                       if frame.columns[col] in ('meaning','explanation')]+[1])
            ws.set_row(row_idx,max(30,lines*15+8))
        for col, value in enumerate(row):
            if pd.isna(value):
                continue
            if isinstance(value,str) and not value:
                continue
            if isinstance(value,(pd.Timestamp,datetime)):
                ws.write_datetime(row_idx,col,value.to_pydatetime() if isinstance(value,pd.Timestamp) else value,date)
            elif isinstance(value,(bool,np.bool_)):
                ws.write_boolean(row_idx,col,bool(value))
            elif isinstance(value,(int,float,np.number)):
                if math.isfinite(float(value)):
                    ws.write_number(row_idx,col,float(value))
            else:
                ws.write_string(row_idx,col,str(value))
    if len(frame):
        ws.add_table(0,0,len(frame),len(frame.columns)-1,{"style":"Table Style Medium 2",
                     "columns":[{"header":c.replace('_',' '),"header_format":header} for c in frame.columns]})
    ws.set_landscape()
    ws.fit_to_pages(1,0)
    ws.repeat_rows(0)
    return ws


def method_frame(manifest, config, qa):
    rows = [
        ("Scope",f"{config['start_month']} to {config['end_month']}; one listing per published monthly snapshot.",""),
        ("Main comparison","Entire home/apt, minimum stay 1–30 nights. Bond reference is ALL dwelling types and ALL bedrooms.",""),
        ("Unit conversion","Weekly bond median / 7 = nightly equivalent. Airbnb minus this benchmark is a descriptive price gap.",""),
        ("Exact temporal join","Join SA2 2019 code and calendar-quarter start, many Airbnb rows to at most one ALL/ALL bond row. No carry-forward.",""),
        ("Geographic alignment","Bond data use SA2 2019. Use official 2019 higher-geography layer 98779 filtered to TA 060, verified against point layer 98970.","https://datafinder.stats.govt.nz/layer/98779/"),
        ("Assignment uncertainty","Airbnb displaces coordinates by up to about 150m. Flag points within 150m of an SA2 boundary and provide an exclusion sensitivity group.","https://insideairbnb.com/data-assumptions/"),
        ("Missing Airbnb prices","Months with no observed Airbnb prices: "+(', '.join(qa['months_without_any_airbnb_prices']) or 'none')+". Retain rows for counts; do not impute prices.","https://insideairbnb.com/get-the-data/"),
        ("Missing bond quarter","Months without an available same-quarter suburb bond release: "+(', '.join(qa['months_without_bond_quarter']) or 'none')+". No carry-forward is used.",manifest["bonds"]["source_page"]),
        ("Property counts","Airbnb counts are snapshot listings. Active bonds are long-term rental stock; Total Bonds is lodgements in a quarter. Neither measures advertised vacancies.",manifest["bonds"]["source_page"]),
        ("Suppression and rounding","Tenancy Services suppresses low-count selections and applies fixed random rounding to base 3. Missing rows and rents are not zeros.",manifest["bonds"]["source_page"]),
        ("Current source caveat","Tenancy Services describes the data as provisional during bond-system migration; recent and earlier releases may not be directly comparable.",manifest["bonds"]["source_page"]),
        ("Outliers","Retain high prices; flag above the monthly room-type 99th percentile. Missing and nonpositive prices are excluded from price calculations only.",""),
        ("Ranking threshold","At least 5 observed matched prices per area and month. This is a stability screen, not a statistical significance test.",""),
        ("Comparability","No bedroom counts in summary Airbnb data. Entire homes improve comparability, but size, quality, fees and occupancy remain unmatched. Gap is not profit or causal impact.",""),
        ("City monthly benchmark","Join official TA 060 monthly bond medians to city summaries by exact month. Difference of medians = city Airbnb median minus city weekly rent /7. This source supports July and August, but supplies no suburb rents.",manifest['city_monthly_bonds']['source_page']),
        ("Separate area benchmark","The listing-weighted matched area benchmark and median listing gap remain separate fields. They require an SA2-quarter match; July/August stay blank. No city rent is copied into an SA2 or listing record.",""),
        ("Offline map","The map uses cached Stats NZ SA2 boundaries, local labels and a distance scale. No external basemap tile requests are made.",""),
        ("Across-month counts","Listing-months are a panel. Do not sum snapshot counts or active-bond stocks as distinct properties across time.",""),
        ("Review dates","Negative days since review are retained and flagged, since publisher date and source review dates can disagree.",""),
        ("Rebuild","Run .venv/bin/python run_pipeline.py. First run or new source retrieval: add --download. Local .env holds the key; no key is exported.",""),
        ("AI assistance","Code and methodology developed with OpenAI ChatGPT through Codex. Validate the implementation and interpret results before coursework submission.",""),
    ]
    if qa.get('airbnb_price_investigation'):
        investigation=qa['airbnb_price_investigation']
        rows.insert(7,('Price recovery investigation',f"Checked all {investigation['checked_snapshots']} detailed NZ snapshots, matching Christchurch City IDs and scrape IDs, plus {investigation['calendar_christchurch_rows_checked']:,} Christchurch calendar rows for wholly missing months. Found {investigation['recoverable_detail_prices']} additional valid prices. December–February price and adjusted_price fields are empty in these source files; no interpolation or other-city substitution. See Price recovery check.",'https://insideairbnb.com/get-the-data/'))
    return pd.DataFrame(rows,columns=["topic","explanation","source_url"])


def price_audit_sheet(wb, frame):
    columns=['snapshot_month','christchurch_listing_count','summary_observed_prices','summary_missing_prices',
             'detail_observed_prices','recoverable_detail_prices','calendar_christchurch_rows',
             'calendar_observed_prices','calendar_observed_adjusted_prices','recovery_status']
    display=frame[columns].copy()
    display['recovery_status']=display.recovery_status.map({
        'source_prices_absent_in_summary_detail_calendar':'Prices absent: summary, detail and calendar',
        'no_additional_same_snapshot_listing_prices':'No additional same-snapshot prices',
        'verified_detail_prices_available':'Verified detailed prices available'})
    ws=table_sheet(wb,'Price recovery check',display)
    wrapped=wb.add_format({'font_name':'Arial','font_size':10,'text_wrap':True,'valign':'vcenter'})
    ws.set_column(9,9,46,wrapped)
    for row in range(1,len(display)+1):ws.set_row(row,32)
    ws.merge_range(len(display)+3,0,len(display)+5,9,
        'Only Christchurch City listing IDs are used. Calendar blanks mean not checked: calendar files were fully scanned for the three wholly missing price snapshots only. Calendar zeroes count observed prices; they are not zero rents. Detailed prices use cents while summary prices are rounded; existing summary prices remain unchanged. Full source paths and row comparisons are in Raw data/inside_airbnb_christchurch_checks/.',wrapped)


def create_workbooks(root, joined, bond_detail, bond_main, city_bonds, area_monthly, city_monthly, audit,
                     coverage, manifest, config, qa, comparison_month, price_audit=None):
    folder=root/'outputs/excel';folder.mkdir(parents=True,exist_ok=True)
    analysis_path=folder/'christchurch_rental_analysis.xlsx'
    dataset_path=folder/'christchurch_merged_datasets.xlsx'
    methods=method_frame(manifest,config,qa)
    sources=pd.DataFrame([{k:v for k,v in s.items() if not isinstance(v,(list,dict))} for s in input_sources(manifest)])
    if 'publisher_scrape_id' in sources:
        sources['publisher_scrape_id']=sources.publisher_scrape_id.astype('string')
    monthly=city_monthly.loc[city_monthly.segment.eq('entire_short_stay')].drop(columns='segment').copy()
    wb=make_workbook(analysis_path)
    overview=wb.add_worksheet('Overview');overview.hide_gridlines(2)
    overview.set_column('A:A',3);overview.set_column('B:B',43);overview.set_column('C:C',24);overview.set_column('D:D',3);overview.set_column('E:O',12)
    title=wb.add_format({'font_name':'Arial','font_size':16,'bold':True,'font_color':'#24323E'})
    text=wb.add_format({'font_name':'Arial','font_size':11,'valign':'vcenter'})
    warning=wb.add_format({'font_name':'Arial','font_size':11,'font_color':'#704919','text_wrap':True,'valign':'vcenter'})
    note=wb.add_format({'font_name':'Arial','font_size':10,'text_wrap':True,'valign':'vcenter'})
    overview.write('B2','Christchurch rental price comparison',title)
    overview.write('B3',f"{config['start_month']} to {config['end_month']}. SA2 2019. NZD.",text)
    source_warning='Airbnb prices unavailable: '+(', '.join(qa['months_without_any_airbnb_prices']) or 'none')+'. Same-quarter suburb bond release unavailable: '+(', '.join(qa['months_without_bond_quarter']) or 'none')+'.'
    overview.set_row(4,44);overview.merge_range('B5:O5',source_warning,warning)
    latest=monthly.iloc[-1]
    metrics=[('Listing-month records',len(joined)),('Distinct listing IDs across period',joined.listing_id.nunique()),
             ('Monthly snapshots',joined.snapshot_month.nunique()),('Christchurch SA2 areas',qa['geography']['polygon_count']),
             ('Latest Airbnb snapshot',str(latest.snapshot_month)),('Latest suburb comparison',comparison_month),
             ('Latest entire short-stay listings',int(latest.listing_count)),
             ('Latest entire short-stay median NZD/night',float(latest.airbnb_median_nightly_nzd)),
             ('Rows assigned to SA2 2019',int(joined.area_code.notna().sum())),
             ('Rows without city SA2 assignment',int(joined.area_code.isna().sum()))]
    for i,(label,value) in enumerate(metrics,7):
        overview.write(i,1,label,text);overview.write(i,2,value,text)
    overview.merge_range('B20:C21','Main group: entire homes with minimum stay ≤30 nights. Bond reference covers all dwelling types and bedroom counts.',note)
    overview.merge_range('B22:C23','Airbnb asking prices and tenancy rents describe different products. The price gap is not profit or evidence of causation.',note)
    overview.write('B25','Latest suburb comparison',title)
    month_rows=area_monthly.loc[area_monthly.snapshot_month.eq(comparison_month)]
    central_all=month_rows.loc[month_rows.segment.eq('all_rooms')&month_rows.area_code.eq('326600')].iloc[0]
    central_primary=month_rows.loc[month_rows.segment.eq('entire_short_stay')&month_rows.area_code.eq('326600')].iloc[0]
    ranked=month_rows.loc[month_rows.segment.eq('entire_short_stay')&month_rows.eligible_gap_ranking].nlargest(1,'median_nightly_gap_nzd')
    results=[('Snapshot',comparison_month),('Central median, all rooms NZD/night',central_all.airbnb_median_nightly_nzd),
             ('Central entire short stays NZD/night',central_primary.airbnb_median_nightly_nzd)]
    if len(ranked):
        best=ranked.iloc[0]
        results += [('Largest eligible entire-home gap',best.area_name),('Median nightly gap NZD',round(best.median_nightly_gap_nzd,2)),('Observed price gaps in that area',int(best.usable_gap_count))]
    for i,(label,value) in enumerate(results,26):
        overview.write(i,1,label,text);overview.write(i,2,value,text)
    overview.write('B35','Latest citywide comparison',title)
    for i,(label,value) in enumerate([
        ('Snapshot',str(latest.snapshot_month)),
        ('City bond median NZD/week',latest.city_bond_weekly_median_nzd),
        ('City bond equivalent NZD/night',round(latest.city_bond_nightly_equivalent_nzd,2)),
        ('Airbnb entire homes NZD/night',latest.airbnb_median_nightly_nzd),
        ('Difference of medians NZD/night',round(latest.citywide_difference_of_medians_nzd,2)),
    ],36):
        overview.write(i,1,label,text);overview.write(i,2,value,text)
    table_sheet(wb,'Monthly trends',monthly)
    late_columns=['snapshot_month','priced_count','airbnb_median_nightly_nzd','city_bond_weekly_median_nzd',
                  'city_bond_nightly_equivalent_nzd','citywide_difference_of_medians_nzd']
    late=monthly.loc[monthly.snapshot_month.isin(['2026-07','2026-08']),late_columns].copy()
    late['suburb_comparison_status']='Unavailable: no same-quarter SA2 bond release'
    late_sheet=table_sheet(wb,'July August comparison',late)
    late_sheet.set_column(6,6,40)
    late_sheet.merge_range('A6:G7','Airbnb group: entire homes with minimum stays of 1–30 nights. City rents are official monthly TA 060 medians. Differences compare citywide medians of different properties; no city rent is copied into a suburb. See Monthly trends for the full period.',note)
    table_sheet(wb,'City monthly bonds',city_bonds)
    table_sheet(wb,'Area monthly',area_monthly)
    table_sheet(wb,'Sensitivity groups',city_monthly)
    table_sheet(wb,'Coverage',coverage)
    table_sheet(wb,'Cleaning audit',audit)
    if price_audit is not None and not price_audit.empty:
        price_audit_sheet(wb,price_audit)
    table_sheet(wb,'Method and sources',methods)
    table_sheet(wb,'Source inventory',sources)
    chart=wb.add_chart({'type':'line'})
    for field,label,color in [('airbnb_median_nightly_nzd','Airbnb entire short stays','#24658A'),
                              ('city_bond_nightly_equivalent_nzd',"Official city monthly bond median ÷7",'#C88329')]:
        col=monthly.columns.get_loc(field)
        chart.add_series({'name':label,'categories':['Monthly trends',1,0,len(monthly),0],
                          'values':['Monthly trends',1,col,len(monthly),col],
                          'line':{'color':color,'width':2},'marker':{'type':'circle','size':4}})
    chart.set_title({'name':'Monthly citywide price benchmarks'});chart.set_y_axis({'name':'NZD per night','min':0})
    chart.set_legend({'position':'bottom'});chart.set_size({'width':820,'height':350});chart.show_blanks_as('gap')
    overview.insert_chart('E7',chart)
    count=wb.add_chart({'type':'column'})
    count.add_series({'name':'Entire short-stay listings','categories':['Monthly trends',1,0,len(monthly),0],
                      'values':['Monthly trends',1,1,len(monthly),1],'fill':{'color':'#24658A'},'border':{'none':True}})
    count.set_title({'name':'Distinct listings in each snapshot'});count.set_y_axis({'min':0,'name':'Listings'})
    count.set_legend({'none':True});count.set_size({'width':820,'height':330});overview.insert_chart('E25',count)
    overview.set_landscape();overview.fit_to_pages(1,1);overview.print_area('A1:O43')
    wb.close()

    wb=make_workbook(dataset_path)
    table_sheet(wb,'Airbnb merged',joined)
    table_sheet(wb,'Bond area quarter',bond_main)
    table_sheet(wb,'Bond category detail',bond_detail)
    table_sheet(wb,'City monthly bonds',city_bonds)
    if price_audit is not None and not price_audit.empty:
        price_audit_sheet(wb,price_audit)
    frames=[joined,bond_main,bond_detail,city_bonds,area_monthly,city_monthly]
    if price_audit is not None:frames.append(price_audit)
    table_sheet(wb,'Field dictionary',dictionary(frames))
    table_sheet(wb,'Method and sources',methods)
    table_sheet(wb,'Source inventory',sources)
    wb.close()
    return [analysis_path,dataset_path]
