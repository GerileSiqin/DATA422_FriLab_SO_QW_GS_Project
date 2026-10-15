"""Protect monthly city geography, exact dates, and the existing SA2 gaps."""
import numpy as np
import pandas as pd
import pytest
from pipeline.city_monthly import clean_city_monthly, add_city_comparisons

CONFIG={'city':'Christchurch City','start_month':'2026-07','end_month':'2026-08'}

def raw(**changes):
    row={'Time Frame':'2026-07-01','Location Id':'60','Location':'Christchurch City',
         'Median Rent':'$550','Lodged Bonds':'1,191','Active Bonds':'42,831','Closed Bonds':'996'}
    row.update(changes)
    return row

def test_filter_exact_city_and_normalise_source_code():
    cleaned=clean_city_monthly(pd.DataFrame([raw(),raw(**{'Location Id':'61','Location':'Other City'})]),CONFIG)
    assert len(cleaned)==1
    assert cleaned.city_code.tolist()==['060']
    assert cleaned.city_active_bonds.iloc[0]==42831
    assert cleaned.city_bond_nightly_equivalent_nzd.iloc[0]==pytest.approx(550/7)

def test_duplicate_city_month_rejected():
    with pytest.raises(ValueError,match='one official'):
        clean_city_monthly(pd.DataFrame([raw(),raw()]),CONFIG)

def test_wrong_city_code_name_rejected():
    with pytest.raises(ValueError,match='Christchurch'):
        clean_city_monthly(pd.DataFrame([raw(Location='Other City')]),CONFIG)

def test_missing_month_not_carried_forward_and_suburb_gap_stays_missing():
    monthly=clean_city_monthly(pd.DataFrame([raw()]),CONFIG)
    summary=pd.DataFrame({'snapshot_month':['2026-07','2026-08'],
        'airbnb_median_nightly_nzd':[249.,246.], 'median_listing_gap_nzd':[np.nan,np.nan]})
    result=add_city_comparisons(summary,monthly)
    assert result.citywide_difference_of_medians_nzd.iloc[0]==pytest.approx(249-550/7)
    assert pd.isna(result.citywide_difference_of_medians_nzd.iloc[1])
    assert result.median_listing_gap_nzd.isna().all()
    assert result.city_monthly_bond_row_available.tolist()==[True,False]

def test_missing_airbnb_price_never_becomes_city_gap():
    monthly=clean_city_monthly(pd.DataFrame([raw()]),CONFIG)
    summary=pd.DataFrame({'snapshot_month':['2026-07'],'airbnb_median_nightly_nzd':[np.nan]})
    assert add_city_comparisons(summary,monthly).citywide_difference_of_medians_nzd.isna().all()
