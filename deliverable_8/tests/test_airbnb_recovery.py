"""No cross-city, cross-snapshot or ambiguous source substitution."""
import pandas as pd
import pytest
from tools.check_airbnb_price_gaps import match_city_details


def frames():
    summary=pd.DataFrame({'id':['1','2'],'neighbourhood_group':['Christchurch City','Auckland'],
                          'price':[None,None]})
    detail=pd.DataFrame({'id':['1','2'],'price':[None,'$500'],'scrape_id':['123','123'],
                         'region_parent_name':['Christchurch City','Auckland'],'detail_source_row':[2,3]})
    return summary,detail


def test_another_city_price_cannot_complete_christchurch():
    summary,detail=frames()
    result,city=match_city_details(summary,detail,{'publisher_scrape_id':'123'})
    assert city.id.tolist()==['1']
    assert result.id.tolist()==['1']
    assert not result.recoverable.any()


def test_exact_source_price_is_a_recovery_candidate():
    summary,detail=frames();detail.loc[0,'price']='$249.00'
    result,_=match_city_details(summary,detail,{'publisher_scrape_id':'123'})
    assert result.recoverable.tolist()==[True]
    assert result.detail_price_nzd.iloc[0]==249


def test_wrong_snapshot_rejected():
    summary,detail=frames()
    with pytest.raises(ValueError,match='scrape ID'):
        match_city_details(summary,detail,{'publisher_scrape_id':'999'})


def test_conflicting_city_geography_rejected():
    summary,detail=frames();detail.loc[0,'region_parent_name']='Auckland'
    with pytest.raises(ValueError,match='geography'):
        match_city_details(summary,detail,{'publisher_scrape_id':'123'})


def test_duplicate_source_keys_rejected():
    summary,detail=frames()
    with pytest.raises(ValueError,match='Duplicate'):
        match_city_details(summary,pd.concat([detail,detail]),{'publisher_scrape_id':'123'})


def test_observed_price_conflicts_cannot_be_silently_overwritten():
    summary,detail=frames();summary.loc[0,'price']='200';detail.loc[0,'price']='250'
    with pytest.raises(ValueError,match='disagree'):
        match_city_details(summary,detail,{'publisher_scrape_id':'123'})


def test_summary_rounding_is_documented_separately_from_a_conflict():
    summary,detail=frames();summary.loc[0,'price']='69';detail.loc[0,'price']='$68.60'
    result,_=match_city_details(summary,detail,{'publisher_scrape_id':'123'})
    assert result.summary_rounding_difference.tolist()==[True]
    assert not result.price_conflict.any()
    assert not result.recoverable.any()
