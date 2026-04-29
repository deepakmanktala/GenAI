import streamlit as st
import pandas as pd
import numpy as np

# ## Title of the application

# st.title("Hello Streamlit from India")

# ## Display a simple text

# st.write("This si a simple text")

# ## Create a simple dataframe


# df = pd.DataFrame({
#     'first_column': [1,2,3,4,5,6],
#     'second_column' : [10,20,30,40,50,60]
# })

# ## display the dataframe
# st.write("Here is the dataframe")
# st.write(df)

# with open('29-04-2025-TO-29-04-2026-BALMLAWRIE-ALL-N.csv', 'r') as file:
#     content = file.read()
#     print(content)


## Page config

st.set_page_config(
    page_title="Balmalawrie Stock Data",
    page_icon="📈📈",
    layout="wide",
)


## Load Data

CSV_PATH = "29-04-2025-TO-29-04-2026-BALMLAWRIE-ALL-N.csv"



@st.cache_data

## @st.cache_data is a decorator — it tells Streamlit to cache (save) the result of the function so it doesn't re-run every time the page refreshes.

def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    '''
    path: str — the path argument should be a string (e.g. "data.csv")
    -> pd.DataFrame — the function will return a pandas DataFrame
    '''
    # now lets strip whitespaces from column names
    df.columns = df.columns.str.strip()

    ## now lets strip white spaces from string values

    str_cols = df.select_dtypes(include="object").columns
    # print(str_cols)

    df[str_cols] = df[str_cols].apply(lambda col: col.str.strip())

    # lets parse Date column
    df["Date"] = pd.to_datetime(df["Date"], dayfirst = True, errors = "coerce")

    ## Now lets clean the Indian comma formatting from NSE data
    for col in ["Total Traded Quantity", "Turnover ₹", "No. of Trades"]:
        if col in df.columns:
            df[col] =(
                df[col].astype(str).str.replace(",","", regex=False).pipe(pd.to_numeric, errors="coerce")
            )

    ## sort by ascending date
    df = df.sort_values("Date").reset_index(drop=True)
    return df

df = load_data(CSV_PATH)

## header 
st.title("📈 BALMLAWRIE — Stock Data")

st.caption(f"NSE | {df['Date'].min().date()} --> {df['Date'].max().date()}  | {len(df)}  trading sessions")
           

## KPI row 
# col1, col2, col3, col4 = st.columns(4)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Last Close",   f"₹ {df['Close Price'].iloc[-1]:,.2f}")
col2.metric("52-Week High", f"₹ {df['High Price'].max():,.2f}")
col3.metric("52-Week Low",  f"₹ {df['Low Price'].min():,.2f}")
col4.metric("Avg Daily Vol", f"{int(df['Total Traded Quantity'].mean()):,} shares")

st.divider()
st.markdown("---") 


# sidebar filters

with st.sidebar:
    st.header(" 🔍 Filters ")

    min_date = df["Date"].min().date()
    max_date = df["Date"].max().date()
    date_range = st.date_input( "Date range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
    columns_to_show = st.multiselect("Columns to display", options=df.columns.tolist(), default=df.columns.tolist())


# Apply date filter
if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
    filtered = df[(df["Date"] >= start) & (df["Date"] <= end)]
else:
    filtered = df.copy()

# ── Main dataframe ─────────────────────────────────────────────────────────────
st.subheader(f"📋 Data  ({len(filtered)} rows)")

display_df = filtered[columns_to_show].copy() if columns_to_show else filtered.copy()

# Format Date for display
if "Date" in display_df.columns:
    display_df["Date"] = display_df["Date"].dt.strftime("%d-%b-%Y")

st.dataframe(
    display_df,
    use_container_width=True,
    height=500,
    hide_index=True,
)

# ── Close price chart ──────────────────────────────────────────────────────────
st.divider()
st.subheader("📉 Close Price — trend")
st.line_chart(filtered.set_index("Date")["Close Price"])

# ── Volume chart ───────────────────────────────────────────────────────────────
st.subheader("📊 Daily Traded Quantity")
st.bar_chart(filtered.set_index("Date")["Total Traded Quantity"])

# ── Summary stats ──────────────────────────────────────────────────────────────
st.divider()
with st.expander("📐 Summary statistics"):
    st.dataframe(
        filtered.describe(include="all").T,
        use_container_width=True,
    )
