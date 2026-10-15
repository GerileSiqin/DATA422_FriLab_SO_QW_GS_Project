"""Regression tests for risks that can materially distort the rental comparison."""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from pipeline.transforms import clean_airbnb,merge_sources,clean_bonds,summarise


def listing(listing_id='1524234450839767037',**values):
    row={'id':listing_id,'name':'Test listing','neighbourhood_group':'Christchurch City',
         'longitude':'172.63','latitude':'-43.53','price':'200','room_type':'Entire home/apt',
         'minimum_nights':'1','availability_365':'0','last_review':'2026-05-20'}
    row.update(values)
    return row


def prepare(tmp_path,rows,month='2026-06'):
    p=tmp_path/'input.csv';pd.DataFrame(rows).to_csv(p,index=False)
    manifest={'airbnb':[{'path':'input.csv','snapshot_date':month+'-19','snapshot_month':month}]}
    config={'city':'Christchurch City','maximum_short_stay_minimum_nights':30}
    return clean_airbnb(tmp_path,manifest,config)


def test_large_identifiers_are_exact_strings(tmp_path):
    frame,_=prepare(tmp_path,[listing()])
    assert frame.iloc[0].listing_id=='1524234450839767037'


def test_missing_and_nonpositive_prices_preserve_listing_counts(tmp_path):
    frame,audit=prepare(tmp_path,[listing('1',price=''),listing('2',price='0'),listing('3',price='-5')])
    assert len(frame)==3
    assert frame.airbnb_nightly_nzd.isna().all()
    assert audit.nonpositive_prices_set_missing.iloc[0]==2


def test_entire_short_stay_definition_does_not_treat_zero_availability_as_missing(tmp_path):
    frame,_=prepare(tmp_path,[listing('1'),listing('2',minimum_nights='31'),listing('3',room_type='Private room')])
    assert frame.entire_short_stay.tolist()==[True,False,False]
    assert not frame.entire_short_stay_with_availability.any()


def test_conflicting_duplicate_ids_fail(tmp_path):
    with pytest.raises(ValueError,match='Conflicting'):
        prepare(tmp_path,[listing('1',price='200'),listing('1',price='250')])


def test_exact_duplicates_counted_and_removed(tmp_path):
    frame,audit=prepare(tmp_path,[listing(),listing()])
    assert len(frame)==1
    assert audit.exact_duplicates_removed.iloc[0]==1


def test_source_dates_define_quarter_and_future_reviews_are_flagged(tmp_path):
    frame,_=prepare(tmp_path,[listing(last_review='2026-07-20')])
    assert frame.quarter_start.iloc[0]==pd.Timestamp('2026-04-01')
    assert bool(frame.review_after_snapshot.iloc[0])


def bond_fixture():
    return pd.DataFrame({'area_code':['326600'],'quarter_start':[pd.Timestamp('2026-04-01')],
                         'bond_weekly_median_nzd':[700.],'bond_nightly_equivalent_nzd':[100.],
                         'bonds_lodged':[30.],'active_bonds':[300.],'closed_bonds':[15.]})


def test_exact_quarter_join_does_not_carry_forward():
    airbnb=pd.DataFrame({'area_code':['326600','326600'],'quarter_start':pd.to_datetime(['2026-04-01','2026-07-01']),
                         'airbnb_nightly_nzd':[200.,200.]})
    result=merge_sources(airbnb,bond_fixture())
    assert len(result)==2
    assert result.nightly_price_gap_nzd.iloc[0]==100.
    assert pd.isna(result.nightly_price_gap_nzd.iloc[1])
    assert result.comparison_status.iloc[1]=='no_bond_row_for_quarter'


def test_many_to_many_bond_join_is_rejected():
    airbnb=pd.DataFrame({'area_code':['326600'],'quarter_start':[pd.Timestamp('2026-04-01')],
                         'airbnb_nightly_nzd':[200.]})
    with pytest.raises(pd.errors.MergeError):
        merge_sources(airbnb,pd.concat([bond_fixture(),bond_fixture()]))


def test_missing_airbnb_price_never_becomes_gap():
    airbnb=pd.DataFrame({'area_code':['326600'],'quarter_start':[pd.Timestamp('2026-04-01')],
                         'airbnb_nightly_nzd':[np.nan]})
    result=merge_sources(airbnb,bond_fixture())
    assert pd.isna(result.nightly_price_gap_nzd.iloc[0])
    assert result.comparison_status.iloc[0]=='airbnb_price_missing'


def test_bond_all_all_selection_does_not_sum_overlapping_categories(tmp_path):
    rows=[]
    for dwelling,beds,rent in [('ALL','ALL','700'),('House','ALL','800'),('ALL','2','600')]:
        rows.append({'TimeFrame':'2026-04-01','Location Id':'326600','Dwelling Type':dwelling,
                     'Number Of Beds':beds,'Median Rent':rent,'Total Bonds':'30','Active Bonds':'300','Closed Bonds':'15'})
    pd.DataFrame(rows).to_csv(tmp_path/'bonds.csv',index=False)
    areas=pd.DataFrame({'area_code':['326600'],'area_name':['Christchurch Central']})
    _,main,_=clean_bonds(tmp_path,{'bonds':{'path':'bonds.csv'}},areas,{'start_month':'2025-10','end_month':'2026-08'})
    assert len(main)==1
    assert main.bond_weekly_median_nzd.iloc[0]==700
    assert main.active_bonds.iloc[0]==300


def test_area_grid_retains_zero_listing_areas_but_missing_snapshot_is_not_zero():
    airbnb=pd.DataFrame({'area_code':['326600'],'quarter_start':[pd.Timestamp('2026-04-01')],
                        'airbnb_nightly_nzd':[200.],'snapshot_month':['2026-06'],'entire_short_stay':[True],
                        'entire_short_stay_with_availability':[False],'near_sa2_boundary':[False]})
    joined=merge_sources(airbnb,bond_fixture())
    areas=pd.DataFrame({'area_code':['326600','326700'],'area_name':['Central','Other']})
    summary,_=summarise(joined,bond_fixture(),areas,{'start_month':'2026-06','end_month':'2026-07','minimum_priced_listings':5})
    empty_area=summary.loc[summary.snapshot_month.eq('2026-06')&summary.area_code.eq('326700')]
    assert empty_area.airbnb_listing_count.eq(0).all()
    missing_month=summary.loc[summary.snapshot_month.eq('2026-07')]
    assert missing_month.airbnb_listing_count.isna().all()
    assert not summary.eligible_gap_ranking.any()
