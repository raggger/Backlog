#!/usr/bin/env python3
"""
update_data.py — run this each day when you receive the new backlog Excel.

Usage:
  python update_data.py path/to/new_backlog.xlsx

It overwrites backlog_data.json in the same folder.
The dashboard will pick up the new data on next page load.
"""

import sys, json, os
from datetime import datetime
import pandas as pd

def age_bucket(m):
    if m < 1:   return 'lt1'
    elif m < 2: return '1to2'
    elif m < 3: return '2to3'
    elif m < 4: return '3to4'
    elif m < 6: return '4to6'
    else:       return '6plus'

def reduction_pct(m):
    if m < 1:   return 0
    elif m <= 2: return 40
    elif m <= 4: return 50
    elif m <= 6: return 0
    else:        return 100

def get_summary(sub_df):
    by_age     = sub_df.groupby('age_bucket').size().to_dict()
    by_product = sub_df.groupby('Product Name').size().sort_values(ascending=False).head(10).to_dict()
    by_cat     = sub_df.groupby('Case Category').size().sort_values(ascending=False).head(6).to_dict()
    by_team    = sub_df.groupby('Case Owner Team').size().sort_values(ascending=False).head(10).to_dict()
    by_rec     = sub_df.groupby('Case Record Type').size().sort_values(ascending=False).to_dict()
    return {
        'total':      int(len(sub_df)),
        'by_age':     {k: int(v) for k, v in by_age.items()},
        'by_product': {k: int(v) for k, v in by_product.items()},
        'by_cat':     {k: int(v) for k, v in by_cat.items()},
        'by_team':    {k: int(v) for k, v in by_team.items()},
        'by_rec':     {k: int(v) for k, v in by_rec.items()},
    }

def main(xlsx_path):
    print(f"Reading: {xlsx_path}")
    df = pd.read_excel(xlsx_path)
    df['Date/Time Opened'] = pd.to_datetime(df['Date/Time Opened'], dayfirst=True, errors='coerce')
    today = pd.Timestamp(datetime.today().date())

    df['age_days']        = (today - df['Date/Time Opened']).dt.days
    df['age_months']      = df['age_days'] / 30.44
    df['age_bucket']      = df['age_months'].apply(age_bucket)
    df['target_reduction']= df['age_months'].apply(reduction_pct)
    df['Date Opened']     = df['Date/Time Opened'].dt.strftime('%d %b %Y')

    cs_df = df[df['Case Record Type'] == 'Client Support']

    action_cols = ['Case Number','Product Name','Case Owner','Account Name',
                   'Case Owner Team','Case Category','Case Record Type',
                   'Date Opened','age_bucket','target_reduction']
    action_df = df[df['age_months'] >= 1][action_cols].copy()
    action_df['Case Number'] = action_df['Case Number'].astype(str)
    action_cases = action_df.to_dict(orient='records')

    output = {
        'snapshot_date': today.strftime('%d %b %Y'),
        'all':           get_summary(df),
        'cs':            get_summary(cs_df),
        'action_cases':  action_cases,
    }

    out_path = os.path.join(os.path.dirname(os.path.abspath(xlsx_path)), 'backlog_data.json')
    # If script is run from repo folder, write there
    local_out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backlog_data.json')
    with open(local_out, 'w') as f:
        json.dump(output, f)

    print(f"✅ Done — {len(df)} total cases, {len(action_cases)} require action.")
    print(f"   Saved to: {local_out}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python update_data.py <path_to_excel.xlsx>")
        sys.exit(1)
    main(sys.argv[1])
