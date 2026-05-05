
import streamlit as st
import pandas as pd
import plotly.express as px
import json

# =========================
# Page config
# =========================
st.set_page_config(
    page_title="NSW Crime Pressure Dashboard",
    page_icon="📊",
    layout="wide"
)

# =========================
# Load data
# =========================
@st.cache_data
def load_data():
    df = pd.read_csv("crime_with_population_2024_onwards.csv")
    df["month"] = pd.to_datetime(df["month"])
    return df

df = load_data()


@st.cache_data
def load_geojson():
    with open("geo/lga_nsw_2024_simplified.geojson", "r", encoding="utf-8") as f:
        return json.load(f)

lga_geojson = load_geojson()


# =========================
# Title and narrative framing
# =========================
st.title("NSW Crime Pressure Dashboard")
st.markdown(
    """
    **Stakeholder:** Local council community safety planners  
    **Narrative question:** Where is crime pressure rising across NSW, what offence types are driving the change, and where should prevention resources be prioritised next?
    """
)

# =========================
# Sidebar filters
# =========================
st.sidebar.header("Filters")

lga_options = sorted(df["lga"].dropna().unique())
selected_lga = st.sidebar.selectbox("Select LGA", lga_options)

offence_options = ["All"] + sorted(df["offence_category"].dropna().unique())
selected_offence = st.sidebar.selectbox("Select offence category", offence_options)

min_month = df["month"].min().date()
max_month = df["month"].max().date()

date_range = st.sidebar.date_input(
    "Select date range",
    value=(min_month, max_month),
    min_value=min_month,
    max_value=max_month
)

trend_metric = st.sidebar.radio(
    "Select trend metric",
    ["Incident count", "Rate per 100k"]
)

# =========================
# Apply filters
# =========================
filtered = df[df["lga"] == selected_lga].copy()

if selected_offence != "All":
    filtered = filtered[filtered["offence_category"] == selected_offence]

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
    filtered = filtered[
        (filtered["month"].dt.date >= start_date) &
        (filtered["month"].dt.date <= end_date)
    ]

# =========================
# KPI calculations
# =========================
total_incidents = int(filtered["incident_count"].sum())

monthly_total = (
    filtered.groupby("month", as_index=False)["incident_count"]
    .sum()
    .sort_values("month")
)

latest_month = monthly_total["month"].max()
latest_incidents = int(monthly_total.loc[monthly_total["month"] == latest_month, "incident_count"].sum())

if len(monthly_total) >= 13:
    latest_value = monthly_total.iloc[-1]["incident_count"]
    previous_year_value = monthly_total.iloc[-13]["incident_count"]
    if previous_year_value != 0:
        yoy_change = ((latest_value - previous_year_value) / previous_year_value) * 100
    else:
        yoy_change = None
else:
    yoy_change = None

top_offence = (
    filtered.groupby("offence_category", as_index=False)["incident_count"]
    .sum()
    .sort_values("incident_count", ascending=False)
)

top_offence_name = top_offence.iloc[0]["offence_category"] if not top_offence.empty else "N/A"

population_value = filtered["population_2024"].dropna().max()

if pd.notna(population_value) and population_value > 0:
    rate_per_100k = total_incidents / population_value * 100000
else:
    rate_per_100k = 0



# ==========================
# Hotspot map
# ==========================
st.header("0. Where: NSW Crime Hotspot Map")

map_filtered = df.copy()

if selected_offence != "All":
    map_filtered = map_filtered[map_filtered["offence_category"] == selected_offence]

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
    map_filtered = map_filtered[
        (map_filtered["month"].dt.date >= start_date) &
        (map_filtered["month"].dt.date <= end_date)
    ]

map_df = (
    map_filtered.groupby("lga", as_index=False)
    .agg(
        incident_count=("incident_count", "sum"),
        population_2024=("population_2024", "max")
    )
)

map_df["rate_per_100k"] = (
    map_df["incident_count"] / map_df["population_2024"] * 100000
)

map_df["rate_per_100k"] = map_df["rate_per_100k"].fillna(0)

map_color_max = map_df["rate_per_100k"].quantile(0.95)

fig_map = px.choropleth_mapbox(
    map_df,
    geojson=lga_geojson,
    locations="lga",
    featureidkey="properties.lga_name",
    color="rate_per_100k",
    range_color=(0, map_color_max),
    hover_name="lga",
    hover_data={
        "incident_count": ":,",
        "population_2024": ":,",
        "rate_per_100k": ":.1f"
    },
    mapbox_style="carto-positron",
    center={"lat": -32.8, "lon": 147.0},
    zoom=5,
    opacity=0.65,
    title="Crime pressure by NSW LGA, rate per 100,000 people"
)

fig_map.update_layout(
    margin={"r": 0, "t": 40, "l": 0, "b": 0},
    height=600
)

st.plotly_chart(fig_map, use_container_width=True)


# =========================
# Executive story section
# =========================
st.header("1. What: Selected Area Crime Snapshot")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Total incidents", f"{total_incidents:,}")
col2.metric("Latest month incidents", f"{latest_incidents:,}")

if yoy_change is not None:
    col3.metric("12-month change", f"{yoy_change:.1f}%")
else:
    col3.metric("12-month change", "N/A")

col4.metric("Rate per 100k", f"{rate_per_100k:,.1f}")
col5.metric("Top offence driver", top_offence_name)

st.markdown(
    f"""
    This section gives a quick overview of **{selected_lga}**.  
    It helps the stakeholder identify whether the selected area has a clear crime pressure signal before exploring deeper patterns.
    """
)

# =========================
# Trend line
# =========================
st.header("2. So What: Monthly Crime Trend")

monthly_total = (
    filtered.groupby("month", as_index=False)
    .agg(
        incident_count=("incident_count", "sum"),
        population_2024=("population_2024", "max")
    )
    .sort_values("month")
)

monthly_total["rate_per_100k"] = (
    monthly_total["incident_count"] / monthly_total["population_2024"] * 100000
)

if trend_metric == "Incident count":
    y_col = "incident_count"
    y_label = "Incident count"
    chart_title = f"Monthly incidents in {selected_lga}"
else:
    y_col = "rate_per_100k"
    y_label = "Rate per 100k people"
    chart_title = f"Monthly crime rate per 100k in {selected_lga}"

fig_trend = px.line(
    monthly_total,
    x="month",
    y=y_col,
    markers=True,
    title=chart_title,
    labels={
        "month": "Month",
        y_col: y_label
    }
)

fig_trend.update_layout(
    xaxis_title="Month",
    yaxis_title=y_label,
    hovermode="x unified"
)

st.plotly_chart(fig_trend, use_container_width=True)

# =========================
# Offence composition
# =========================
st.header("3. Why: Offence Composition")

offence_summary = (
    filtered.groupby("offence_category", as_index=False)["incident_count"]
    .sum()
    .sort_values("incident_count", ascending=False)
)

fig_bar = px.bar(
    offence_summary,
    x="incident_count",
    y="offence_category",
    orientation="h",
    title=f"Offence categories driving incidents in {selected_lga}",
    hover_data=["incident_count"]
)

fig_bar.update_layout(
    xaxis_title="Incident count",
    yaxis_title="Offence category",
    yaxis={"categoryorder": "total ascending"}
)

st.plotly_chart(fig_bar, use_container_width=True)

# =========================
# Selected area detail panel
# =========================
st.header("4. What Next: Selected Area Detail Panel")

latest_data = filtered[filtered["month"] == latest_month]

latest_by_offence = (
    latest_data.groupby("offence_category", as_index=False)["incident_count"]
    .sum()
    .sort_values("incident_count", ascending=False)
)

st.subheader(f"Insight card for {selected_lga}")

if not latest_by_offence.empty:
    latest_top = latest_by_offence.iloc[0]
    st.info(
        f"""
        In the latest available month, **{latest_top['offence_category']}** was the largest offence category in **{selected_lga}**, 
        with **{int(latest_top['incident_count']):,} incidents**.
        
        This suggests that prevention planning should first examine the main offence driver rather than treating all crime types as one general problem.
        """
    )
else:
    st.warning("No data available for the selected filters.")

# =========================
# Data preview
# =========================
with st.expander("Show filtered data"):
    st.dataframe(filtered.head(200))
