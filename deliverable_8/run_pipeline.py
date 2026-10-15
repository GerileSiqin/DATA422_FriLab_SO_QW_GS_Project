"""Build the complete Christchurch rental comparison with one command."""
from __future__ import annotations

import argparse
import json
import logging
import platform
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parent


def run(allow_download=False):
    from pipeline.sources import prepare_inputs,save_json,digest
    from pipeline.geography import get_city_polygons,assign_areas
    from pipeline.transforms import clean_airbnb,clean_bonds,merge_sources,summarise
    from pipeline.city_monthly import load_city_monthly,add_city_comparisons
    from pipeline.price_investigation import load_price_investigation
    from pipeline.validation import coverage_table,validate_analysis,verify_workbooks
    from pipeline.figures import create_figures
    from pipeline.maps import create_map
    from pipeline.workbooks import create_workbooks
    config=json.loads((ROOT/'config/project.json').read_text())
    output=ROOT/'outputs';output.mkdir(exist_ok=True)
    save_json(output/'run_status.json',{'status':'running','started_at_utc':datetime.now(timezone.utc).isoformat()})
    LOG=logging.getLogger('pipeline')
    LOG.info('1/7 Verify or download source snapshots')
    manifest=prepare_inputs(ROOT,config,allow_download)
    city_bonds,city_source=load_city_monthly(ROOT,config,allow_download)
    manifest['city_monthly_bonds']=city_source
    price_audit,price_investigation,investigation_sources=load_price_investigation(ROOT,config,manifest)
    if price_investigation:
        manifest['airbnb_price_investigation_sources']=investigation_sources
    save_json(ROOT/'data/raw/source_manifest.json',manifest)
    LOG.info('2/7 Load Koordinates geography and clean data')
    areas=get_city_polygons(ROOT,config,allow_download)
    airbnb,audit=clean_airbnb(ROOT,manifest,config)
    LOG.info('3/7 Assign SA2 areas and check API sample')
    enriched,geoqa=assign_areas(airbnb,areas,ROOT,config,allow_download)
    detail,bonds,bondqa=clean_bonds(ROOT,manifest,areas,config)
    joined=merge_sources(enriched,bonds)
    LOG.info('4/7 Aggregate monthly comparisons and validate')
    area_monthly,city_monthly=summarise(joined,bonds,areas,config)
    city_monthly=add_city_comparisons(city_monthly,city_bonds)
    coverage=coverage_table(joined,bonds,config)
    coverage=coverage.merge(city_bonds[['snapshot_month','city_bond_weekly_median_nzd']],on='snapshot_month',how='left',validate='one_to_one')
    coverage['city_monthly_bond_available']=coverage.city_bond_weekly_median_nzd.notna()
    if price_investigation:
        coverage=coverage.merge(price_audit[['snapshot_month','detail_observed_prices','recoverable_detail_prices','recovery_status']],on='snapshot_month',how='left',validate='one_to_one')
    checks=validate_analysis(ROOT,manifest,joined,bonds,area_monthly,city_monthly,audit,areas,config)
    geoqa['polygon_count']=len(areas)
    qa={'geography':geoqa,'bonds':bondqa,'checks':checks,
        'airbnb_listing_months':len(joined),'unique_listing_ids':joined.listing_id.nunique(),
        'missing_airbnb_months':manifest['missing_airbnb_months'],
        'months_without_any_airbnb_prices':coverage.loc[coverage.all_prices_missing,'snapshot_month'].tolist(),
        'months_without_bond_quarter':coverage.loc[~coverage.bond_quarter_available,'snapshot_month'].tolist(),
        'months_without_city_monthly_rent':coverage.loc[~coverage.city_monthly_bond_available,'snapshot_month'].tolist()}
    if price_investigation:
        qa['airbnb_price_investigation']=price_investigation
    tables={'airbnb_merged':joined,'bond_detailed':detail,'bond_area_quarter':bonds,
            'area_monthly':area_monthly,'city_monthly':city_monthly,'city_bond_monthly':city_bonds,'cleaning_audit':audit,'coverage':coverage}
    if price_investigation:
        tables['airbnb_price_recovery_audit']=price_audit
    table_dir=output/'tables';table_dir.mkdir(exist_ok=True)
    for name,frame in tables.items():
        frame.to_csv(table_dir/f'{name}.csv',index=False,float_format='%.10g')
    with sqlite3.connect(output/'christchurch_rentals.sqlite') as con:
        for name,frame in tables.items():
            frame.to_sql(name,con,index=False,if_exists='replace')
        con.execute('CREATE UNIQUE INDEX IF NOT EXISTS listing_month_key ON airbnb_merged(listing_id,snapshot_month)')
        con.execute('CREATE UNIQUE INDEX IF NOT EXISTS bond_area_quarter_key ON bond_area_quarter(area_code,quarter_start)')
    LOG.info('5/7 Create figures and interactive map')
    figures,comparison_month=create_figures(ROOT,joined,area_monthly,city_monthly,areas,config)
    map_path=create_map(ROOT,area_monthly,city_monthly,areas,joined.snapshot_month.max(),allow_download)
    LOG.info('6/7 Export Excel workbooks and GIS layers')
    books=create_workbooks(ROOT,joined,detail,bonds,city_bonds,area_monthly,city_monthly,audit,coverage,manifest,config,qa,comparison_month,price_audit=price_audit)
    import geopandas as gpd
    gis=output/'gis';gis.mkdir(exist_ok=True)
    gpkg=gis/'christchurch_rental_comparison.gpkg'
    latest=joined.snapshot_month.max()
    for month,name in [(comparison_month,'latest_comparable_areas'),(latest,'latest_snapshot_areas')]:
        frame=area_monthly.loc[area_monthly.snapshot_month.eq(month)&area_monthly.segment.eq('entire_short_stay')]
        areas.merge(frame,on=['area_code','area_name'],validate='one_to_one').to_file(gpkg,layer=name,driver='GPKG')
    point_frame=joined.copy()
    for col in point_frame.select_dtypes(include='category').columns:
        point_frame[col]=point_frame[col].astype('string')
    points=gpd.GeoDataFrame(point_frame,geometry=gpd.points_from_xy(point_frame.longitude,point_frame.latitude),crs=4326)
    points.to_file(gpkg,layer='airbnb_listing_months',driver='GPKG')
    LOG.info('7/7 Verify exported data and write completion manifest')
    qa['export_checks']=verify_workbooks(books,joined,detail,bonds,area_monthly,coverage,city_bonds,city_monthly)
    with sqlite3.connect(output/'christchurch_rentals.sqlite') as con:
        qa['export_checks']['sqlite_listing_count']=con.execute('SELECT COUNT(*) FROM airbnb_merged').fetchone()[0]==len(joined)
        sql=con.execute('SELECT COUNT(*) FROM airbnb_merged a LEFT JOIN bond_area_quarter b ON a.area_code=b.area_code AND a.quarter_start=b.quarter_start').fetchone()[0]
        qa['export_checks']['sqlite_join_does_not_inflate']=sql==len(joined)
    qa['latest_comparable_month']=comparison_month
    qa['latest_airbnb_month']=latest
    qa['latest_citywide_comparison_month']=city_monthly.loc[city_monthly.citywide_difference_of_medians_nzd.notna(),'snapshot_month'].max()
    save_json(output/'data_quality.json',qa)
    codes=[ROOT/'run_pipeline.py',ROOT/'config/project.json',ROOT/'requirements.txt',*sorted((ROOT/'pipeline').glob('*.py')),
           *sorted((ROOT/'tools').glob('*.py')),*sorted((ROOT/'tests').glob('*.py')),
           ROOT/'pipeline/map_template.html']
    artifacts=[p for p in output.rglob('*') if p.is_file() and p.suffix in ('.xlsx','.png','.pdf','.csv','.html','.sqlite','.gpkg')]
    result={'status':'complete','completed_at_utc':datetime.now(timezone.utc).isoformat(),'python':platform.python_version(),
            'config':config,'inputs':manifest,'code_sha256':{str(p.relative_to(ROOT)):digest(p) for p in codes},
            'artifacts':{str(p.relative_to(ROOT)):{'sha256':digest(p),'bytes':p.stat().st_size} for p in artifacts},
            'analysis_checks':checks,'export_checks':qa['export_checks'],
            'scope_complete_snapshots':not manifest['missing_airbnb_months'],
            'limitations':{'price_missing_months':qa['months_without_any_airbnb_prices'],
                           'bond_quarter_missing_months':qa['months_without_bond_quarter']}}
    save_json(output/'run_manifest.json',result)
    save_json(output/'run_status.json',{'status':'complete','completed_at_utc':result['completed_at_utc']})
    LOG.info('Complete: %s listing-months, %s unique listings, %s areas',len(joined),joined.listing_id.nunique(),len(areas))
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--download',action='store_true',help='Fetch missing public inputs and allow Koordinates/API validation requests')
    args=parser.parse_args()
    logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(message)s',datefmt='%H:%M:%S')
    try:
        run(args.download)
    except Exception as exc:
        from pipeline.sources import save_json
        # Application errors never include credential-bearing URLs or response bodies.
        save_json(ROOT/'outputs/run_status.json',{'status':'failed','error_type':type(exc).__name__})
        logging.error('%s: %s',type(exc).__name__,exc)
        return 1
    return 0


if __name__=='__main__':
    sys.exit(main())
