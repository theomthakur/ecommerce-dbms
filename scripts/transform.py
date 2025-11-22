import pandas as pd


def _clean_numeric_series(s: pd.Series) -> pd.Series:
    s2 = s.astype(str).str.strip()
    # Convert parentheses to negative sign
    s2 = s2.str.replace(r"^\((.*)\)$", r"-\1", regex=True)
    # Remove any character except digits, dot and minus
    s2 = s2.str.replace(r"[^0-9\-.]", "", regex=True)
    return pd.to_numeric(s2, errors='coerce')


def clean_orders(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce')
    df['Ship Date'] = pd.to_datetime(df['Ship Date'], errors='coerce')
    str_cols = ['Order ID','Ship Mode','Customer ID','Customer Name','Segment','Postal Code','City','State','Country','Region','Market','Product ID','Category','Sub-Category','Product Name','Order Priority']
    for c in str_cols:
        if c in df.columns:
            df[c] = df[c].astype(str).str.strip()
    for col in ['Sales','Quantity','Discount','Profit','Shipping Cost']:
        if col in df.columns:
            df[col] = _clean_numeric_series(df[col])
    return df


def clean_returns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [c.strip() for c in df.columns]
    # Normalize common columns
    if 'Returned' in df.columns and 'Order ID' in df.columns:
        df = df.rename(columns={'Returned':'returned_flag', 'Order ID':'order_id'})
    elif len(df.columns) >= 2:
        df = df.rename(columns={df.columns[0]:'returned_flag', df.columns[1]:'order_id'})
    df['order_id'] = df['order_id'].astype(str).str.strip()
    return df
