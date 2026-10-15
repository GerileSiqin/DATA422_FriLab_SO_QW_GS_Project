"""Read saved deliverables and independently verify provenance and arithmetic."""
import json
import sqlite3
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from pipeline.sources import digest,save_json,input_sources
from statistics import median


def main():
    manifest=json.loads((ROOT/'outputs/run_manifest.json').read_text())
    checks={'run_completed':manifest['status']=='complete'}
    checks['source_hashes_match']=all(digest(ROOT/x['path'])==x['sha256']
                                     for x in input_sources(manifest['inputs']))
    checks['output_hashes_match']=all(digest(ROOT/path)==details['sha256']
                                     for path,details in manifest['artifacts'].items())
    checks['code_hashes_match']=all(digest(ROOT/path)==expected for path,expected in manifest['code_sha256'].items())
    with sqlite3.connect(ROOT/'outputs/christchurch_rentals.sqlite') as con:
        count=con.execute('SELECT COUNT(*) FROM airbnb_merged').fetchone()[0]
        checks['sqlite_calendar_quarters']=con.execute('''SELECT COUNT(*) FROM airbnb_merged
            WHERE CAST(strftime('%m',snapshot_date) AS INTEGER) NOT BETWEEN
            CAST(strftime('%m',quarter_start) AS INTEGER) AND CAST(strftime('%m',quarter_start) AS INTEGER)+2''').fetchone()[0]==0
        checks['sqlite_exact_bond_join']=con.execute('''SELECT COUNT(*) FROM airbnb_merged a
            LEFT JOIN bond_area_quarter b ON a.area_code=b.area_code AND a.quarter_start=b.quarter_start
            WHERE a.bond_row_matched != (b.area_code IS NOT NULL)
            OR ABS(a.bond_weekly_median_nzd-b.bond_weekly_median_nzd)>0.00000001''').fetchone()[0]==0
        checks['sqlite_gap_arithmetic']=con.execute('''SELECT COUNT(*) FROM airbnb_merged WHERE
            ABS(nightly_price_gap_nzd-(airbnb_nightly_nzd-bond_weekly_median_nzd/7.0))>0.00000001''').fetchone()[0]==0
        checks['sqlite_null_prices_stay_null']=con.execute('''SELECT COUNT(*) FROM airbnb_merged
            WHERE (airbnb_nightly_nzd IS NULL OR bond_weekly_median_nzd IS NULL) AND nightly_price_gap_nzd IS NOT NULL''').fetchone()[0]==0
        checks['citywide_monthly_comparisons_independent']=True
        for month in ['2026-07','2026-08']:
            prices=[r[0] for r in con.execute('SELECT airbnb_nightly_nzd FROM airbnb_merged WHERE snapshot_month=? AND entire_short_stay=1 AND airbnb_nightly_nzd IS NOT NULL',(month,))]
            rent=con.execute('SELECT city_bond_weekly_median_nzd FROM city_bond_monthly WHERE snapshot_month=?',(month,)).fetchone()[0]
            exported=con.execute("SELECT citywide_difference_of_medians_nzd FROM city_monthly WHERE snapshot_month=? AND segment='entire_short_stay'",(month,)).fetchone()[0]
            checks['citywide_monthly_comparisons_independent'] &= abs(exported-(median(prices)-rent/7))<1e-8
        checks['july_august_suburb_gaps_stay_null']=con.execute("SELECT COUNT(*) FROM area_monthly WHERE snapshot_month IN ('2026-07','2026-08') AND (bond_weekly_median_nzd IS NOT NULL OR median_nightly_gap_nzd IS NOT NULL)").fetchone()[0]==0
        checks['monthly_city_source_has_unique_months']=con.execute('SELECT COUNT(*)=COUNT(DISTINCT snapshot_month) FROM city_bond_monthly').fetchone()[0]==1
        checks['only_christchurch_listing_records']=con.execute("SELECT COUNT(*) FROM airbnb_merged WHERE neighbourhood_group IS NULL OR TRIM(neighbourhood_group)!='Christchurch City'").fetchone()[0]==0
        if con.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='airbnb_price_recovery_audit'").fetchone()[0]:
            checks['source_audit_counts_reconcile']=True
            for month,total,observed,missing in con.execute('SELECT snapshot_month,christchurch_listing_count,summary_observed_prices,summary_missing_prices FROM airbnb_price_recovery_audit'):
                actual=con.execute('SELECT COUNT(*),COUNT(airbnb_nightly_nzd) FROM airbnb_merged WHERE snapshot_month=?',(month,)).fetchone()
                checks['source_audit_counts_reconcile'] &= (total,observed,missing)==(actual[0],actual[1],actual[0]-actual[1])
            checks['three_missing_months_checked_in_calendar']=con.execute("SELECT COUNT(*) FROM airbnb_price_recovery_audit WHERE calendar_checked=1 AND calendar_christchurch_rows>0 AND calendar_observed_prices=0 AND calendar_observed_adjusted_prices=0 AND snapshot_month IN ('2025-12','2026-01','2026-02')").fetchone()[0]==3
            checks['source_audit_no_false_completion']=con.execute('SELECT SUM(recoverable_detail_prices) FROM airbnb_price_recovery_audit').fetchone()[0]==0
    map_html=(ROOT/'outputs/maps/christchurch_price_bars.html').read_text()
    checks['map_has_no_external_tile_layer']='L.tileLayer' not in map_html and 'tile.openstreetmap.org' not in map_html
    checks['map_contains_monthly_city_comparisons']='const cityRecords=' in map_html and '__CITY_RECORDS__' not in map_html
    with sqlite3.connect(ROOT/'outputs/gis/christchurch_rental_comparison.gpkg') as con:
        checks['gpkg_point_count']=con.execute('SELECT COUNT(*) FROM airbnb_listing_months').fetchone()[0]==count
        checks['gpkg_172_areas']=con.execute('SELECT COUNT(*) FROM latest_comparable_areas').fetchone()[0]==172
    # Read protected credential only for a yes/no absence scan; never print it.
    from dotenv import dotenv_values
    key=dotenv_values(ROOT/'.env').get('KOORDINATES_API_KEY','')
    leaks=[]
    if key and key!='PASTE_YOUR_KEY_HERE':
        import zipfile
        for folder in ['outputs','data/cache']:
            for path in (ROOT/folder).rglob('*'):
                if not path.is_file():continue
                if path.suffix=='.xlsx':
                    with zipfile.ZipFile(path) as z:
                        if any(key.encode() in z.read(n) for n in z.namelist()):leaks.append(str(path.relative_to(ROOT)))
                elif key.encode() in path.read_bytes():leaks.append(str(path.relative_to(ROOT)))
    checks['no_api_key_in_outputs_or_cache']=not leaks
    report={'checks':checks,'all_passed':all(checks.values()),'listing_month_count':count}
    save_json(ROOT/'outputs/verification_report.json',report)
    print(json.dumps(report,indent=2))
    return 0 if report['all_passed'] else 1


if __name__=='__main__':sys.exit(main())
