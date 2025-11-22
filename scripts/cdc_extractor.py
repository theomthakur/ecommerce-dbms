"""Simple CDC extractor that computes new order rows between snapshots.

Usage:
  python scripts/cdc_extractor.py --new data/cleaned_orders.csv --prev data/cleaned_orders_prev.csv --out data/changes_new_orders.csv
If `--prev` does not exist the script will create the prev snapshot and exit.
"""
import argparse
from pathlib import Path
import pandas as pd


def compute_delta(new_path: Path, prev_path: Path, out_path: Path):
    new = pd.read_csv(new_path, dtype=str)
    if not prev_path.exists():
        # create snapshot and exit
        new.to_csv(prev_path, index=False)
        print(f'Created snapshot {prev_path}; no delta to compute.')
        return
    prev = pd.read_csv(prev_path, dtype=str)
    # Use Order ID as primary key for delta
    key = 'Order ID' if 'Order ID' in new.columns else 'OrderID'
    new_ids = set(new[key].astype(str))
    prev_ids = set(prev[key].astype(str))
    added_ids = new_ids - prev_ids
    delta = new[new[key].astype(str).isin(added_ids)].copy()
    delta.to_csv(out_path, index=False)
    # update prev snapshot to new
    new.to_csv(prev_path, index=False)
    print(f'Wrote delta with {len(delta)} rows to {out_path}; updated snapshot {prev_path}')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--new', required=True)
    parser.add_argument('--prev', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    compute_delta(Path(args.new), Path(args.prev), Path(args.out))


if __name__ == '__main__':
    main()
