"""Load the optional, hash-verified source investigation without imputing prices."""
import json
from pathlib import Path
import pandas as pd
from .sources import digest


def load_price_investigation(root: Path, config: dict, source_manifest: dict):
    path=root/'Raw data/inside_airbnb_christchurch_checks/investigation_manifest.json'
    if not path.exists():
        return pd.DataFrame(),None,[]
    inventory=json.loads(path.read_text())
    if inventory['city']!=config['city'] or inventory['country']!='New Zealand' or inventory['scope']!=source_manifest['scope']:
        raise ValueError('Price investigation has a different city, country or time scope')
    recorded={s['path']:s['sha256'] for s in inventory['summary_sources']}
    current={s['path']:s['sha256'] for s in source_manifest['airbnb']}
    if recorded!=current:
        raise ValueError('Price investigation refers to different source snapshot revisions; rerun its script')
    audit_source=inventory['audit_file']
    if digest(root/audit_source['path'])!=audit_source['sha256']:
        raise ValueError('Price investigation audit CSV hash changed')
    audit=pd.read_csv(root/audit_source['path'])
    if audit.snapshot_month.duplicated().any() or set(audit.snapshot_month)!=set(s['snapshot_month'] for s in source_manifest['airbnb']):
        raise ValueError('Price investigation does not cover each snapshot exactly once')
    sources=inventory['archive_sources']+[
        {**audit_source,'source':'Christchurch same-snapshot price recovery audit'},
        {'path':str(path.relative_to(root)),'sha256':digest(path),'source':'Christchurch source investigation manifest'}]
    summary={'checked_at_utc':inventory['checked_at_utc'],'checked_snapshots':len(audit),
        'recoverable_detail_prices':int(audit.recoverable_detail_prices.sum()),
        'calendar_christchurch_rows_checked':int(audit.calendar_christchurch_rows.sum()),
        'all_null_months_verified_in_calendar':audit.loc[audit.recovery_status.eq('source_prices_absent_in_summary_detail_calendar'),'snapshot_month'].tolist(),
        'audit_path':audit_source['path']}
    if summary['recoverable_detail_prices']:
        raise ValueError('Investigation found recovery candidates; review and integrate exact source prices before rebuilding')
    return audit,summary,sources
