import streamlit as st
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine, text
import plotly.express as px
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DW_DB = ROOT / 'dw.db'


def _get_engine():
    return create_engine(f'sqlite:///{DW_DB}')


@st.cache_data
def load_categories():
    engine = _get_engine()
    q = "SELECT DISTINCT category FROM dim_product ORDER BY category"
    df = pd.read_sql_query(q, engine)
    cats = ['All'] + df['category'].dropna().tolist()
    return cats


@st.cache_data
def load_regions():
    engine = _get_engine()
    q = "SELECT DISTINCT region FROM dim_region ORDER BY region"
    df = pd.read_sql_query(q, engine)
    regs = ['All'] + df['region'].dropna().tolist()
    return regs


@st.cache_data
def load_date_bounds():
    engine = _get_engine()
    q = "SELECT MIN(date) AS min_date, MAX(date) AS max_date FROM dim_date"
    df = pd.read_sql_query(q, engine)
    min_date = pd.to_datetime(df.at[0, 'min_date'])
    max_date = pd.to_datetime(df.at[0, 'max_date'])
    return min_date, max_date


@st.cache_data
def load_monthly_sales_filtered(category='All', region='All', start=None, end=None):
    engine = _get_engine()
    where_clauses = []
    if category and category != 'All':
        where_clauses.append(f"p.category = '{category.replace("'","''")}'")
    if region and region != 'All':
        where_clauses.append(f"r.region = '{region.replace("'","''")}'")
    if start is not None and end is not None:
        # date_key is YYYYMMDD integer; convert to strings
        start_key = int(pd.to_datetime(start).strftime('%Y%m%d'))
        end_key = int(pd.to_datetime(end).strftime('%Y%m%d'))
        where_clauses.append(f"d.date_key BETWEEN {start_key} AND {end_key}")
    where_sql = (' AND '.join(where_clauses)) if where_clauses else '1=1'
    q = f"""
    SELECT d.year, d.month, COALESCE(SUM(f.sales),0) AS total_sales
    FROM fact_sales f
    JOIN dim_date d ON f.date_key = d.date_key
    LEFT JOIN dim_product p ON f.product_key = p.product_key
    LEFT JOIN dim_region r ON f.region_key = r.region_key
    WHERE {where_sql}
    GROUP BY d.year, d.month
    ORDER BY d.year, d.month
    """
    df = pd.read_sql_query(q, engine)
    df['month_str'] = df['year'].astype(str) + '-' + df['month'].astype(str).str.zfill(2)
    df['month_dt'] = pd.to_datetime(df['month_str'])
    return df


@st.cache_data
def load_kpis(category='All', region='All', start=None, end=None):
    engine = _get_engine()
    where_clauses = []
    if category and category != 'All':
        where_clauses.append(f"p.category = '{category.replace("'","''")}'")
    if region and region != 'All':
        where_clauses.append(f"r.region = '{region.replace("'","''")}'")
    if start is not None and end is not None:
        start_key = int(pd.to_datetime(start).strftime('%Y%m%d'))
        end_key = int(pd.to_datetime(end).strftime('%Y%m%d'))
        where_clauses.append(f"d.date_key BETWEEN {start_key} AND {end_key}")
    where_sql = (' AND '.join(where_clauses)) if where_clauses else '1=1'
    q = f"""
    SELECT COALESCE(SUM(f.sales),0) AS total_sales, COALESCE(COUNT(DISTINCT f.order_id),0) AS total_orders
    FROM fact_sales f
    JOIN dim_date d ON f.date_key = d.date_key
    LEFT JOIN dim_product p ON f.product_key = p.product_key
    LEFT JOIN dim_region r ON f.region_key = r.region_key
    WHERE {where_sql}
    """
    df = pd.read_sql_query(q, engine)
    total_sales = float(df.at[0, 'total_sales']) if not df.empty else 0.0
    total_orders = int(df.at[0, 'total_orders']) if not df.empty else 0
    avg_order = (total_sales / total_orders) if total_orders else 0.0
    return {'total_sales': total_sales, 'total_orders': total_orders, 'avg_order': avg_order}


@st.cache_data
def load_top_products(limit=20, category='All', region='All'):
    engine = _get_engine()
    where_clauses = []
    if category and category != 'All':
        where_clauses.append(f"p.category = '{category.replace("'","''")}'")
    if region and region != 'All':
        where_clauses.append(f"r.region = '{region.replace("'","''")}'")
    where_sql = (' AND '.join(where_clauses)) if where_clauses else '1=1'
    q = f"""
    SELECT p.product_name, COALESCE(SUM(f.sales),0) AS total_sales
    FROM fact_sales f
    LEFT JOIN dim_product p ON f.product_key = p.product_key
    LEFT JOIN dim_region r ON f.region_key = r.region_key
    WHERE {where_sql}
    GROUP BY p.product_name
    ORDER BY total_sales DESC
    LIMIT {int(limit)}
    """
    return pd.read_sql_query(q, engine)


@st.cache_data
def load_product_time_series(product_name):
    engine = _get_engine()
    prod = product_name.replace("'","''")
    q = f"""
    SELECT d.year, d.month, COALESCE(SUM(f.sales),0) AS total_sales
    FROM fact_sales f
    JOIN dim_date d ON f.date_key = d.date_key
    JOIN dim_product p ON f.product_key = p.product_key
    WHERE p.product_name = '{prod}'
    GROUP BY d.year, d.month
    ORDER BY d.year, d.month
    """
    df = pd.read_sql_query(q, engine)
    if df.empty:
        return df
    df['month_str'] = df['year'].astype(str) + '-' + df['month'].astype(str).str.zfill(2)
    df['month_dt'] = pd.to_datetime(df['month_str'])
    return df


# --- Additional analysis helpers ---


@st.cache_data
def load_sales_by_category(category='All', region='All', start=None, end=None):
    engine = _get_engine()
    where_clauses = []
    if category and category != 'All':
        where_clauses.append(f"p.category = '{category.replace("'","''")}'")
    if region and region != 'All':
        where_clauses.append(f"r.region = '{region.replace("'","''")}'")
    if start is not None and end is not None:
        start_key = int(pd.to_datetime(start).strftime('%Y%m%d'))
        end_key = int(pd.to_datetime(end).strftime('%Y%m%d'))
        where_clauses.append(f"d.date_key BETWEEN {start_key} AND {end_key}")
    where_sql = (' AND '.join(where_clauses)) if where_clauses else '1=1'
    q = f"""
    SELECT p.category, COALESCE(SUM(f.sales),0) AS total_sales, COUNT(DISTINCT f.order_id) AS orders
    FROM fact_sales f
    LEFT JOIN dim_product p ON f.product_key = p.product_key
    LEFT JOIN dim_region r ON f.region_key = r.region_key
    LEFT JOIN dim_date d ON f.date_key = d.date_key
    WHERE {where_sql}
    GROUP BY p.category
    ORDER BY total_sales DESC
    """
    return pd.read_sql_query(q, engine)


@st.cache_data
def load_order_value_distribution(category='All', region='All', start=None, end=None):
    engine = _get_engine()
    where_clauses = []
    if category and category != 'All':
        where_clauses.append(f"p.category = '{category.replace("'","''")}'")
    if region and region != 'All':
        where_clauses.append(f"r.region = '{region.replace("'","''")}'")
    if start is not None and end is not None:
        start_key = int(pd.to_datetime(start).strftime('%Y%m%d'))
        end_key = int(pd.to_datetime(end).strftime('%Y%m%d'))
        where_clauses.append(f"d.date_key BETWEEN {start_key} AND {end_key}")
    where_sql = (' AND '.join(where_clauses)) if where_clauses else '1=1'
    q = f"""
    SELECT f.order_id, COALESCE(SUM(f.sales),0) AS order_total
    FROM fact_sales f
    LEFT JOIN dim_product p ON f.product_key = p.product_key
    LEFT JOIN dim_region r ON f.region_key = r.region_key
    LEFT JOIN dim_date d ON f.date_key = d.date_key
    WHERE {where_sql}
    GROUP BY f.order_id
    """
    return pd.read_sql_query(q, engine)


@st.cache_data
def load_top_customers(limit=10, category='All', region='All', start=None, end=None):
    engine = _get_engine()
    where_clauses = []
    if category and category != 'All':
        where_clauses.append(f"p.category = '{category.replace("'","''")}'")
    if region and region != 'All':
        where_clauses.append(f"r.region = '{region.replace("'","''")}'")
    if start is not None and end is not None:
        start_key = int(pd.to_datetime(start).strftime('%Y%m%d'))
        end_key = int(pd.to_datetime(end).strftime('%Y%m%d'))
        where_clauses.append(f"d.date_key BETWEEN {start_key} AND {end_key}")
    where_sql = (' AND '.join(where_clauses)) if where_clauses else '1=1'
    q = f"""
    SELECT c.customer_name, COALESCE(SUM(f.sales),0) AS total_sales, COUNT(DISTINCT f.order_id) AS orders
    FROM fact_sales f
    LEFT JOIN dim_customer c ON f.customer_key = c.customer_key
    LEFT JOIN dim_product p ON f.product_key = p.product_key
    LEFT JOIN dim_region r ON f.region_key = r.region_key
    LEFT JOIN dim_date d ON f.date_key = d.date_key
    WHERE {where_sql}
    GROUP BY c.customer_name
    ORDER BY total_sales DESC
    LIMIT {int(limit)}
    """
    return pd.read_sql_query(q, engine)


@st.cache_data
def load_returns_df():
    p = ROOT / 'data' / 'cleaned_returns.csv'
    if not p.exists():
        return pd.DataFrame(columns=['returned_flag','order_id','Region'])
    df = pd.read_csv(p)
    # Normalize column names
    df.columns = [c.strip() for c in df.columns]
    return df


@st.cache_data
def load_returns_rate_by_category(start=None, end=None):
    # Uses DW fact_sales and dim_product to compute orders by category and matches returned order ids from CSV
    engine = _get_engine()
    returns = load_returns_df()
    if returns.empty:
        return pd.DataFrame(columns=['category','orders','returned_orders','return_rate'])
    returned_orders = set(returns['order_id'].dropna().unique().tolist())
    q = f"""
    SELECT p.category, COUNT(DISTINCT f.order_id) AS orders
    FROM fact_sales f
    LEFT JOIN dim_product p ON f.product_key = p.product_key
    LEFT JOIN dim_date d ON f.date_key = d.date_key
    GROUP BY p.category
    """
    df_orders = pd.read_sql_query(q, engine)
    # Count returned orders per category by querying fact_sales for orders present in returned_orders
    if not returned_orders:
        df_orders['returned_orders'] = 0
        df_orders['return_rate'] = 0.0
        return df_orders
    # Create a temporary in-memory table of returned order ids
    # Simpler approach: fetch mapping of order_id->category and compute in pandas
    q2 = f"""
    SELECT f.order_id, p.category
    FROM fact_sales f
    LEFT JOIN dim_product p ON f.product_key = p.product_key
    """
    df_map = pd.read_sql_query(q2, engine)
    df_map = df_map.drop_duplicates(subset=['order_id'])
    df_map['is_returned'] = df_map['order_id'].isin(returned_orders)
    df_ret = df_map.groupby('category')['is_returned'].agg(['sum','count']).rename(columns={'sum':'returned_orders','count':'orders'}).reset_index()
    df_ret['return_rate'] = df_ret['returned_orders'] / df_ret['orders'].replace({0:pd.NA})
    # Merge with totals to ensure all categories present
    df_out = df_orders.merge(df_ret[['category','returned_orders','return_rate']], on='category', how='left')
    df_out['returned_orders'] = df_out['returned_orders'].fillna(0).astype(int)
    df_out['return_rate'] = df_out['return_rate'].fillna(0.0)
    return df_out


st.title('E-Commerce DW Dashboard')
st.markdown('Interactive dashboard reading the local `dw.db`. Use the sidebar to filter and drill down.')

# Check DW DB exists
if not DW_DB.exists():
    st.error(f"Data warehouse file not found: {DW_DB}\nRun `scripts/build_dw.py` or the ETL to create `dw.db` before using the dashboard.")
    st.stop()

# Sidebar filters
st.sidebar.header('Filters')
cats = load_categories()
regions = load_regions()
min_date, max_date = load_date_bounds()
sel_category = st.sidebar.selectbox('Category', options=cats)
sel_region = st.sidebar.selectbox('Region', options=regions)
sel_date = st.sidebar.date_input('Date range', value=(min_date, max_date))
# Top N control
top_n = st.sidebar.slider('Top N products', min_value=5, max_value=50, value=20, step=5)

# Load and show monthly sales with filters
df_month = load_monthly_sales_filtered(category=sel_category, region=sel_region, start=sel_date[0], end=sel_date[1])

# KPI summary
kpis = load_kpis(category=sel_category, region=sel_region, start=sel_date[0], end=sel_date[1])
col1, col2, col3 = st.columns(3)
col1.metric('Total Sales', f"${kpis['total_sales']:,.2f}")
col2.metric('Total Orders', f"{kpis['total_orders']:,}")
col3.metric('Avg Order Value', f"${kpis['avg_order']:,.2f}")

fig = px.line(df_month, x='month_dt', y='total_sales', title='Monthly Sales')
st.plotly_chart(fig, width='stretch')

# Download filtered monthly sales
if not df_month.empty:
    csv = df_month.to_csv(index=False)
    st.download_button('Download monthly sales CSV', csv, file_name='monthly_sales_filtered.csv', mime='text/csv')

st.header('Top Products')
df_top = load_top_products(top_n, category=sel_category, region=sel_region)
fig2 = px.bar(df_top, x='product_name', y='total_sales', title='Top Products by Sales')
fig2.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig2, width='stretch')

# Product drilldown
st.subheader('Product Drilldown')
prod_options = [''] + df_top['product_name'].tolist()
sel_prod = st.selectbox('Select product for time series', options=prod_options)
if sel_prod:
    prod_ts = load_product_time_series(sel_prod)
    if not prod_ts.empty:
        fig3 = px.line(prod_ts, x='month_dt', y='total_sales', title=f'Sales for {sel_prod}')
        st.plotly_chart(fig3, width='stretch')
    else:
        st.write('No data for selected product')

st.caption('Note: Filters are applied to queries; performance depends on `dw.db` size.')

# --- Additional analysis visualizations ---

st.header('Category Breakdown')
df_cat = load_sales_by_category(category=sel_category, region=sel_region, start=sel_date[0], end=sel_date[1])
if not df_cat.empty:
    # Treemap gives hierarchical view (category -> sales)
    fig_cat = px.treemap(df_cat, path=['category'], values='total_sales', title='Sales by Category')
    st.plotly_chart(fig_cat, width='stretch')
else:
    st.write('No category sales data')

st.header('Order Value Distribution')
df_orders = load_order_value_distribution(category=sel_category, region=sel_region, start=sel_date[0], end=sel_date[1])
if not df_orders.empty:
    bins = st.slider('Histogram bins', min_value=10, max_value=200, value=50)
    log_y = st.checkbox('Log scale Y axis (helpful for skewed distributions)', value=False)
    fig_hist = px.histogram(df_orders, x='order_total', nbins=bins, title='Order Value Distribution')
    if log_y:
        fig_hist.update_yaxes(type='log')
    st.plotly_chart(fig_hist, width='stretch')
else:
    st.write('No order-level data available')

st.header('Returns Analysis')
df_returns_rate = load_returns_rate_by_category(start=sel_date[0], end=sel_date[1])
if not df_returns_rate.empty:
    df_returns_rate['return_rate_pct'] = df_returns_rate['return_rate'] * 100
    fig_ret = px.bar(df_returns_rate.sort_values('return_rate', ascending=False), x='category', y='return_rate_pct',
                     title='Return Rate by Category (%)', text='returned_orders')
    fig_ret.update_layout(yaxis_title='Return Rate (%)')
    st.plotly_chart(fig_ret, width='stretch')
    st.markdown('**Returned orders sample:**')
    sample_ret = load_returns_df().head(10)
    st.dataframe(sample_ret)
else:
    st.write('No returns data (check `data/cleaned_returns.csv`)')

st.header('Top Customers')
top_k = st.slider('Top K customers', min_value=5, max_value=50, value=10, step=5)
df_cust = load_top_customers(limit=top_k, category=sel_category, region=sel_region, start=sel_date[0], end=sel_date[1])
if not df_cust.empty:
    fig_cust = px.bar(df_cust, x='customer_name', y='total_sales', title=f'Top {top_k} Customers by Sales')
    fig_cust.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_cust, width='stretch')
else:
    st.write('No customer data available')
