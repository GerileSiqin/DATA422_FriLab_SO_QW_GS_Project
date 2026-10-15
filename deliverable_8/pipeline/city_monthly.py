"""Keep official monthly city benchmarks separate from SA2-quarter benchmarks."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from .sources import digest
from .transforms import number, require_columns


def clean_city_monthly(frame: pd.DataFrame, config: dict) -> pd.DataFrame:
    require_columns(frame, ['Time Frame','Location Id','Location','Median Rent',
                             'Lodged Bonds','Active Bonds','Closed Bonds'], 'Monthly territorial-authority data')
    frame=frame.copy()
    frame['source_row']=frame.index+2
    codes=frame['Location Id'].astype('string').str.strip().str.zfill(3)
    city=frame.loc[codes.eq('060')].copy()
    if not city.Location.str.strip().eq(config['city']).all():
        raise ValueError('TA 060 does not consistently identify Christchurch City')
    dates=pd.to_datetime(city['Time Frame'],errors='raise')
    city['snapshot_month']=dates.dt.strftime('%Y-%m')
    city=city.loc[city.snapshot_month.between(config['start_month'],config['end_month'])].copy()
    if city.empty or city.snapshot_month.duplicated().any():
        raise ValueError('Expected one official Christchurch city bond record per month')
    mapping={'Median Rent':'city_bond_weekly_median_nzd',
             'Geometric Mean Rent':'city_bond_weekly_geomean_nzd',
             'Lower Quartile Rent':'city_bond_weekly_lower_quartile_nzd',
             'Upper Quartile Rent':'city_bond_weekly_upper_quartile_nzd',
             'Lodged Bonds':'city_bonds_lodged','Active Bonds':'city_active_bonds','Closed Bonds':'city_closed_bonds'}
    result=city[['snapshot_month','source_row']].copy()
    result['city_code']='060'
    result['city_name']=config['city']
    result['benchmark_geography']='territorial_authority'
    result['benchmark_frequency']='monthly'
    for source,target in mapping.items():
        if source not in city:
            continue
        result[target]=number(city[source])
        if target.startswith('city_bond_weekly'):
            result.loc[result[target].le(0),target]=np.nan
        elif result[target].dropna().lt(0).any():
            raise ValueError(f'Negative monthly city bond count in {source}')
    result['city_bond_nightly_equivalent_nzd']=result.city_bond_weekly_median_nzd/7
    return result.sort_values('snapshot_month').reset_index(drop=True)


def load_city_monthly(root: Path, config: dict, allow_download: bool):
    inventory=root/'Raw data/tenancy_download_manifest.json'
    if not inventory.exists() and allow_download:
        from tools.download_tenancy_raw import main
        main()
    if not inventory.exists():
        raise ValueError('Monthly city source is missing. Run tools/download_tenancy_raw.py or use --download')
    records=json.loads(inventory.read_text())['files']
    matches=[r for r in records if r['category']=='monthly_territorial_authority']
    if len(matches)!=1:
        raise ValueError('Expected one monthly territorial-authority source in download manifest')
    source=matches[0].copy()
    path=root/source['path']
    if digest(path)!=source['sha256']:
        raise ValueError('The monthly territorial-authority source hash has changed')
    frame=pd.read_csv(path,dtype='string',encoding=source.get('encoding','utf-8-sig'),na_values=['NULL'])
    result=clean_city_monthly(frame,config)
    result['source_file']=source['path']
    source.update(source='MBIE Tenancy Services monthly TA data',source_page=json.loads(inventory.read_text())['source_page'])
    return result,source


def add_city_comparisons(city_summary: pd.DataFrame, monthly: pd.DataFrame) -> pd.DataFrame:
    columns=['snapshot_month','city_bond_weekly_median_nzd','city_bond_nightly_equivalent_nzd',
             'city_active_bonds','city_bonds_lodged']
    result=city_summary.merge(monthly[columns],on='snapshot_month',how='left',validate='many_to_one',indicator='_city_join')
    result['city_monthly_bond_row_available']=result.pop('_city_join').eq('both')
    result['citywide_difference_of_medians_nzd']=result.airbnb_median_nightly_nzd-result.city_bond_nightly_equivalent_nzd
    result['citywide_ratio_of_medians']=result.airbnb_median_nightly_nzd/result.city_bond_nightly_equivalent_nzd
    # Existing median_listing_gap_nzd and area benchmarks are deliberately untouched.
    return result
