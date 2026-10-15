"""Audit official same-snapshot detailed/calendar files for Christchurch prices.

Preserves publisher archives and Christchurch-only extracts. Does not substitute
another city, another snapshot, modelled revenue or future calendar averages.
"""
from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from pipeline.sources import digest,save_json
from pipeline.transforms import number,require_columns


def fetch_archive(url, path, allow_download):
    if not path.exists():
        if not allow_download:
            raise ValueError(f'Missing local archive: {path.name}; run with --download')
        path.parent.mkdir(parents=True,exist_ok=True)
        temporary=path.with_suffix(path.suffix+'.tmp')
        with requests.get(url,stream=True,timeout=(15,90)) as response:
            response.raise_for_status()
            with temporary.open('wb') as dest:
                for block in response.iter_content(1024*1024):
                    dest.write(block)
        temporary.replace(path)
    return {'path':str(path.relative_to(ROOT)),'url':url,'sha256':digest(path),'bytes':path.stat().st_size,
            'source':'Inside Airbnb price-gap investigation'}


def match_city_details(summary, detailed, source):
    """The snapshot's Christchurch-labelled IDs and region name must agree."""
    require_columns(summary,['id','neighbourhood_group','price'],'Summary')
    require_columns(detailed,['id','price','scrape_id'],'Detailed listings')
    city=summary.loc[summary.neighbourhood_group.str.strip().eq('Christchurch City')].copy()
    if city.id.duplicated().any() or detailed.id.duplicated().any():
        raise ValueError('Duplicate listing IDs; refusing an ambiguous recovery join')
    detail_city=detailed.loc[detailed.id.isin(set(city.id))].copy()
    if 'region_parent_name' in detail_city:
        if not detail_city.region_parent_name.str.strip().eq('Christchurch City').all():
            raise ValueError('Detailed listing geography conflicts with Christchurch summary')
    if 'neighbourhood_group_cleansed' in detail_city:
        if not detail_city.neighbourhood_group_cleansed.str.strip().eq('Christchurch City').all():
            raise ValueError('Detailed listing geography conflicts with Christchurch summary')
    scrape=source.get('publisher_scrape_id')
    if scrape is not None and not detail_city.scrape_id.eq(str(scrape)).all():
        raise ValueError('Detailed scrape ID differs from the summary snapshot')
    left=city[['id','price']].rename(columns={'price':'summary_price_raw'})
    right=detail_city[['id','price','detail_source_row']].rename(columns={'price':'detail_price_raw'})
    comparison=left.merge(right,on='id',how='left',validate='one_to_one',indicator=True)
    comparison['summary_price_nzd']=number(comparison.summary_price_raw)
    comparison['detail_price_nzd']=number(comparison.detail_price_raw)
    comparison['recoverable']=~comparison.summary_price_nzd.gt(0) & comparison.detail_price_nzd.gt(0)
    both=comparison.summary_price_nzd.gt(0)&comparison.detail_price_nzd.gt(0)
    difference=(comparison.summary_price_nzd-comparison.detail_price_nzd).abs()
    # Summary exports round detailed cents to whole NZD. Record this precision
    # loss separately; it is not a new missing price or a conflicting quote.
    comparison['summary_rounding_difference']=both & difference.gt(1e-8) & difference.le(.50000001) & comparison.summary_price_nzd.mod(1).eq(0)
    comparison['price_conflict']=both & difference.gt(1e-8) & ~comparison.summary_rounding_difference
    if comparison.price_conflict.any():
        raise ValueError('Observed prices disagree between same-snapshot sources')
    return comparison,detail_city


def inspect_snapshot(source, allow_download, folder):
    date=source['snapshot_date'];month=source['snapshot_month']
    summary=pd.read_csv(ROOT/source['path'],dtype='string')
    url=f'https://data.insideairbnb.com/new-zealand/{date}/data/listings.csv.gz'
    archive=ROOT/f'data/raw/airbnb/detailed/{date}_listings.csv.gz'
    detail_source=fetch_archive(url,archive,allow_download)
    fields=['id','price','scrape_id','last_scraped','region_name','region_parent_name',
            'region_parent_parent_name','neighbourhood_group_cleansed','latitude','longitude']
    detail=pd.read_csv(archive,dtype='string',usecols=lambda c:c in fields)
    detail['detail_source_row']=detail.index+2
    comparison,city=match_city_details(summary,detail,source)
    extract=folder/f'{date}_christchurch_detailed_price_check.csv'
    city.to_csv(extract,index=False)
    comparisons=folder/f'{date}_christchurch_price_comparison.csv'
    comparison.drop(columns='_merge').to_csv(comparisons,index=False)
    result={'snapshot_month':month,'snapshot_date':date,'christchurch_listing_count':len(comparison),
        'summary_observed_prices':int(comparison.summary_price_nzd.gt(0).sum()),
        'summary_missing_prices':int((~comparison.summary_price_nzd.gt(0)).sum()),
        'detail_matched_listings':int(comparison['_merge'].eq('both').sum()),
        'detail_observed_prices':int(comparison.detail_price_nzd.gt(0).sum()),
        'recoverable_detail_prices':int(comparison.recoverable.sum()),
        'detail_price_conflicts':int(comparison.price_conflict.sum()),
        'summary_rounding_difference_count':int(comparison.summary_rounding_difference.sum()),
        'calendar_checked':False,'calendar_christchurch_rows':None,
        'calendar_observed_prices':None,'calendar_observed_adjusted_prices':None,
        'detailed_source_file':str(archive.relative_to(ROOT)),
        'christchurch_extract':str(extract.relative_to(ROOT)),
        'listing_comparison_file':str(comparisons.relative_to(ROOT))}
    sources=[detail_source]
    # For wholly missing months, inspect every Christchurch calendar record.
    if result['summary_observed_prices']==0:
        cal_url=f'https://data.insideairbnb.com/new-zealand/{date}/data/calendar.csv.gz'
        cal=ROOT/f'data/raw/airbnb/calendar/{date}_calendar.csv.gz'
        sources.append(fetch_archive(cal_url,cal,allow_download))
        ids=set(comparison.id)
        counts={'rows':0,'price':0,'adjusted_price':0}
        observed_ids=set();first_date=None;last_date=None
        cal_extract=folder/f'{date}_christchurch_calendar.csv.gz'
        import gzip
        with gzip.open(cal_extract,'wt') as dest:
            first=True
            for block in pd.read_csv(cal,dtype='string',chunksize=400000):
                require_columns(block,['listing_id','date','price','adjusted_price'],'Calendar')
                selected=block.loc[block.listing_id.isin(ids)]
                if selected.empty:continue
                counts['rows']+=len(selected)
                for field in ['price','adjusted_price']:
                    valid=number(selected[field]).gt(0)
                    counts[field]+=int(valid.sum())
                    observed_ids.update(selected.loc[valid,'listing_id'])
                low=selected.date.min();high=selected.date.max()
                first_date=min(first_date,low) if first_date else low
                last_date=max(last_date,high) if last_date else high
                selected.to_csv(dest,index=False,header=first);first=False
        result.update(calendar_checked=True,calendar_christchurch_rows=counts['rows'],
            calendar_observed_prices=counts['price'],calendar_observed_adjusted_prices=counts['adjusted_price'],
            calendar_listings_with_price=len(observed_ids),calendar_first_date=first_date,calendar_last_date=last_date,
            calendar_christchurch_extract=str(cal_extract.relative_to(ROOT)))
    result['recovery_status']='verified_detail_prices_available' if result['recoverable_detail_prices'] else (
        'source_prices_absent_in_summary_detail_calendar' if result['calendar_checked'] and not result['calendar_observed_prices'] and not result['calendar_observed_adjusted_prices'] else 'no_additional_same_snapshot_listing_prices')
    return result,sources


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--download',action='store_true')
    args=parser.parse_args()
    manifest=json.loads((ROOT/'data/raw/source_manifest.json').read_text())
    folder=ROOT/'Raw data/inside_airbnb_christchurch_checks';folder.mkdir(parents=True,exist_ok=True)
    results=[];sources=[]
    with ThreadPoolExecutor(max_workers=3) as pool:
        jobs=[pool.submit(inspect_snapshot,s,args.download,folder) for s in manifest['airbnb']]
        for job in as_completed(jobs):
            result,archives=job.result();results.append(result);sources.extend(archives)
            print(f"{result['snapshot_month']}: {result['recoverable_detail_prices']} recoverable prices; {result['recovery_status']}",flush=True)
    results.sort(key=lambda x:x['snapshot_month'])
    table=folder/'airbnb_price_recovery_audit.csv'
    pd.DataFrame(results).to_csv(table,index=False)
    save_json(folder/'investigation_manifest.json',{
        'checked_at_utc':datetime.now(timezone.utc).isoformat(),'city':'Christchurch City','country':'New Zealand',
        'source_page':'https://insideairbnb.com/get-the-data/','scope':manifest['scope'],
        'method':'Exact same-snapshot listing IDs from Christchurch City summary, with scrape and detailed geographic checks. Full Christchurch calendar scans for entirely missing price months. No interpolation, revenue-derived prices, city substitution or temporal substitution.',
        'summary_sources':manifest['airbnb'],'archive_sources':sorted(sources,key=lambda x:x['path']),
        'audit_file':{'path':str(table.relative_to(ROOT)),'sha256':digest(table)},'results':results,
        'recoverable_price_count':sum(r['recoverable_detail_prices'] for r in results)})
    print('Investigation saved:',table.relative_to(ROOT))


if __name__=='__main__':main()
