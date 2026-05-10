
import streamlit as st
import pandas as pd
import plotly.express as px
import json

COLOR_SCALE = "Blues"

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
    df = pd.read_csv("crime_with_population_socioeconomic_2024_onwards.csv")
    df["month"] = pd.to_datetime(df["month"])
    return df

df = load_data()


@st.cache_data
def load_geojson():
    with open("geo/lga_nsw_2024_simplified.geojson", "r", encoding="utf-8") as f:
        return json.load(f)

lga_geojson = load_geojson()


def get_lga_map_view(geojson, lga_names):
    if not lga_names:
        return {"lat": -32.8, "lon": 147.0}, 5
    name_set = set(lga_names)
    all_lons, all_lats = [], []
    for feature in geojson["features"]:
        if feature["properties"].get("lga_name") in name_set:
            geom = feature["geometry"]
            coords = []
            if geom["type"] == "Polygon":
                for ring in geom["coordinates"]:
                    coords.extend(ring)
            elif geom["type"] == "MultiPolygon":
                for polygon in geom["coordinates"]:
                    for ring in polygon:
                        coords.extend(ring)
            all_lons.extend(c[0] for c in coords)
            all_lats.extend(c[1] for c in coords)
    if not all_lons:
        return {"lat": -32.8, "lon": 147.0}, 5
    center = {"lat": sum(all_lats) / len(all_lats), "lon": sum(all_lons) / len(all_lons)}
    extent = max(max(all_lons) - min(all_lons), max(all_lats) - min(all_lats))
    if extent > 5:
        zoom = 6
    elif extent > 2:
        zoom = 7
    elif extent > 1:
        zoom = 8
    elif extent > 0.5:
        zoom = 9
    else:
        zoom = 10
    return center, zoom


def make_sparkline(series):
    bars = "▁▂▃▄▅▆▇█"
    vals = list(series)
    if len(vals) < 2:
        return "—"
    mn, mx = min(vals), max(vals)
    if mn == mx:
        return bars[3] * min(8, len(vals))
    return "".join(bars[min(7, int((v - mn) / (mx - mn) * 7.99))] for v in vals[-8:])


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

lga_only = sorted(df["lga"].dropna().unique())
selected_lgas = st.sidebar.multiselect(
    "Select LGA(s)",
    lga_only,
    placeholder="All LGAs (default)"
)

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

st.sidebar.divider()
st.sidebar.caption("Export")
_sidebar_csv_placeholder = st.sidebar.empty()

# =========================
# Apply filters
# =========================
filtered = df[df["lga"].isin(selected_lgas)].copy() if selected_lgas else df.copy()

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

pop_total = filtered.groupby("lga")["population_2024"].max().sum()

if pd.notna(pop_total) and pop_total > 0:
    rate_per_100k = total_incidents / pop_total * 100000
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

# Sparklines per LGA for rich tooltips
monthly_by_lga = (
    map_filtered.groupby(["lga", "month"])["incident_count"]
    .sum().reset_index().sort_values(["lga", "month"])
)
sparklines = (
    monthly_by_lga.groupby("lga")["incident_count"]
    .apply(make_sparkline).reset_index()
    .rename(columns={"incident_count": "trend"})
)
top_off_map = (
    map_filtered.groupby(["lga", "offence_category"])["incident_count"]
    .sum().reset_index()
    .sort_values("incident_count", ascending=False)
    .drop_duplicates("lga")[["lga", "offence_category"]]
    .rename(columns={"offence_category": "top_offence"})
)
map_df = map_df.merge(sparklines, on="lga", how="left")
map_df = map_df.merge(top_off_map, on="lga", how="left")
map_df["trend"] = map_df["trend"].fillna("—")
map_df["top_offence"] = map_df["top_offence"].fillna("N/A")

map_color_max = map_df["rate_per_100k"].quantile(0.95)

map_center, map_zoom = get_lga_map_view(lga_geojson, selected_lgas)

fig_map = px.choropleth_mapbox(
    map_df,
    geojson=lga_geojson,
    locations="lga",
    featureidkey="properties.lga_name",
    color="rate_per_100k",
    range_color=(0, map_color_max),
    hover_name="lga",
    custom_data=["incident_count", "population_2024", "rate_per_100k", "top_offence", "trend"],
    mapbox_style="carto-positron",
    center=map_center,
    zoom=map_zoom,
    color_continuous_scale=COLOR_SCALE,
    opacity=0.65,
    title="Crime pressure by NSW LGA, rate per 100,000 people"
)

fig_map.update_traces(
    hovertemplate=(
        "<b>%{hovertext}</b><br>"
        "Rate per 100k: <b>%{customdata[2]:.1f}</b><br>"
        "Total incidents: %{customdata[0]:,}<br>"
        "Population: %{customdata[1]:,}<br>"
        "Top offence: %{customdata[3]}<br>"
        "Trend (últimos 8 meses): %{customdata[4]}"
        "<extra></extra>"
    )
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

if not selected_lgas:
    lga_label = "all NSW LGAs"
elif len(selected_lgas) == 1:
    lga_label = selected_lgas[0]
else:
    lga_label = f"{len(selected_lgas)} selected LGAs"

_sidebar_csv_placeholder.download_button(
    label="Download filtered data as CSV",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name=f"nsw_crime_{lga_label.replace(' ', '_')}.csv",
    mime="text/csv"
)

st.markdown(
    f"""
    This section gives a quick overview of **{lga_label}**.
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
    chart_title = f"Monthly incidents in {lga_label}"
else:
    y_col = "rate_per_100k"
    y_label = "Rate per 100k people"
    chart_title = f"Monthly crime rate per 100k in {lga_label}"

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
    title=f"Offence categories driving incidents in {lga_label}",
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

st.subheader(f"Insight card for {lga_label}")

if not latest_by_offence.empty:
    latest_top = latest_by_offence.iloc[0]
    st.info(
        f"""
        In the latest available month, **{latest_top['offence_category']}** was the largest offence category in **{lga_label}**,
        with **{int(latest_top['incident_count']):,} incidents**.

        This suggests that prevention planning should first examine the main offence driver rather than treating all crime types as one general problem.
        """
    )
else:
    st.warning("No data available for the selected filters.")

# =========================
# Seasonality heatmap
# =========================
st.header("5. Seasonality: Crime by Month of Year")

seasonal = filtered.copy()
seasonal["month_name"] = seasonal["month"].dt.month
seasonal["year"] = seasonal["month"].dt.year

heat_pivot = (
    seasonal.groupby(["year", "month_name"], as_index=False)["incident_count"]
    .sum()
    .pivot(index="year", columns="month_name", values="incident_count")
)

month_abbr = {1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
              7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"}
heat_pivot.columns = [month_abbr[c] for c in heat_pivot.columns]

fig_heat = px.imshow(
    heat_pivot,
    labels={"x": "Month", "y": "Year", "color": "Incidents"},
    title=f"Crime seasonality in {lga_label} — total incidents by month and year",
    color_continuous_scale=COLOR_SCALE,
    text_auto=True,
    aspect="auto"
)
fig_heat.update_layout(margin={"t": 50, "b": 0})

st.plotly_chart(fig_heat, use_container_width=True)

# =========================
# LGA comparator
# =========================
st.header("6. Comparator: Side-by-Side LGA Comparison")

comp_lga_options = ["All"] + sorted(df["lga"].dropna().unique())
default_lga_b = comp_lga_options.index("Sydney") if "Sydney" in comp_lga_options else 0

comp_col1, comp_col2, comp_col3 = st.columns([2, 2, 2])
with comp_col1:
    lga_a = st.selectbox("LGA A", comp_lga_options, key="lga_a")
with comp_col2:
    lga_b = st.selectbox("LGA B", comp_lga_options, index=default_lga_b, key="lga_b")
with comp_col3:
    comp_offence = st.selectbox("Offence category", offence_options, key="comp_offence")

def get_lga_monthly(lga_name, offence):
    d = df.copy() if lga_name == "All" else df[df["lga"] == lga_name].copy()
    if offence != "All":
        d = d[d["offence_category"] == offence]
    if isinstance(date_range, tuple) and len(date_range) == 2:
        s, e = date_range
        d = d[(d["month"].dt.date >= s) & (d["month"].dt.date <= e)]
    if lga_name == "All":
        pop_by_month = df.groupby(["month", "lga"], as_index=False)["population_2024"].max()
        total_pop = pop_by_month.groupby("month", as_index=False)["population_2024"].sum()
        incidents = d.groupby("month", as_index=False)["incident_count"].sum()
        return incidents.merge(total_pop, on="month").sort_values("month")
    return (
        d.groupby("month", as_index=False)
        .agg(incident_count=("incident_count", "sum"), population_2024=("population_2024", "max"))
        .sort_values("month")
    )

comp_a = get_lga_monthly(lga_a, comp_offence)
comp_a["lga"] = lga_a
comp_b = get_lga_monthly(lga_b, comp_offence)
comp_b["lga"] = lga_b

comp_df = pd.concat([comp_a, comp_b], ignore_index=True)
comp_df["rate_per_100k"] = comp_df["incident_count"] / comp_df["population_2024"] * 100000

comp_left, comp_right = st.columns(2)

with comp_left:
    fig_comp_trend = px.line(
        comp_df,
        x="month",
        y="rate_per_100k",
        color="lga",
        color_discrete_sequence=["#1f77b4", "#ff7f0e"],
        markers=True,
        title=f"Monthly rate per 100k: {lga_a} vs {lga_b}",
        labels={"month": "Month", "rate_per_100k": "Rate per 100k", "lga": "LGA"}
    )
    fig_comp_trend.update_layout(hovermode="x unified")
    st.plotly_chart(fig_comp_trend, use_container_width=True)

with comp_right:
    offence_a = (df if lga_a == "All" else df[df["lga"] == lga_a]).groupby("offence_category", as_index=False)["incident_count"].sum()
    offence_a["lga"] = lga_a
    offence_b = (df if lga_b == "All" else df[df["lga"] == lga_b]).groupby("offence_category", as_index=False)["incident_count"].sum()
    offence_b["lga"] = lga_b
    offence_comp = pd.concat([offence_a, offence_b], ignore_index=True)

    fig_comp_bar = px.bar(
        offence_comp,
        x="incident_count",
        y="offence_category",
        color="lga",
        color_discrete_sequence=["#1f77b4", "#ff7f0e"],
        barmode="group",
        orientation="h",
        title=f"Offence composition: {lga_a} vs {lga_b}",
        labels={"incident_count": "Incidents", "offence_category": "Offence", "lga": "LGA"}
    )
    fig_comp_bar.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig_comp_bar, use_container_width=True)

# =========================
# Socioeconomic context
# =========================
st.header("7. So What: Socioeconomic Context")

st.markdown(
    """
    This section connects crime pressure with socioeconomic context from the 2021 Census.
    It helps stakeholders move beyond **where crime is happening** and explore whether high-crime LGAs also show different income or housing-cost patterns.
    """
)

socio_lga = (
    filtered.dropna(subset=[
        "median_household_income_weekly",
        "median_rent_weekly",
        "median_mortgage_repay_monthly",
        "rate_per_100k",
        "population_2024"
    ])
    .groupby("lga", as_index=False)
    .agg(
        incident_count=("incident_count", "sum"),
        population_2024=("population_2024", "max"),
        rate_per_100k=("rate_per_100k", "sum"),
        median_household_income_weekly=("median_household_income_weekly", "max"),
        median_rent_weekly=("median_rent_weekly", "max"),
        median_mortgage_repay_monthly=("median_mortgage_repay_monthly", "max")
    )
)

fig_socio = px.scatter(
    socio_lga,
    x="median_household_income_weekly",
    y="rate_per_100k",
    size="population_2024",
    hover_name="lga",
    hover_data={
        "incident_count": ":,",
        "population_2024": ":,",
        "rate_per_100k": ":.1f",
        "median_household_income_weekly": ":,.0f",
        "median_rent_weekly": ":,.0f",
        "median_mortgage_repay_monthly": ":,.0f"
    },
    labels={
        "median_household_income_weekly": "Median household income per week",
        "rate_per_100k": "Crime rate per 100k people",
        "population_2024": "Population"
    },
    title="Crime rate compared with median household income by LGA"
)

fig_socio.update_layout(
    xaxis_title="Median household income per week",
    yaxis_title="Crime rate per 100k people",
    hovermode="closest"
)

st.plotly_chart(fig_socio, use_container_width=True)

st.info(
    "Interpretation: This view does not prove causation, but it helps identify whether high crime pressure appears alongside different income and housing-cost conditions. These patterns can guide deeper stakeholder discussion and prevention planning."
)

# =========================
# LGA ranking
# =========================
st.header("8. Ranking: LGAs by Crime Rate")

rank_col1, rank_col2 = st.columns([2, 1])
with rank_col1:
    rank_offence = st.selectbox("Filter by offence category", offence_options, key="rank_offence")
with rank_col2:
    top_n = st.slider("Show top N LGAs", min_value=5, max_value=50, value=20, step=5)

rank_df = df.copy()
if rank_offence != "All":
    rank_df = rank_df[rank_df["offence_category"] == rank_offence]
if isinstance(date_range, tuple) and len(date_range) == 2:
    s, e = date_range
    rank_df = rank_df[(rank_df["month"].dt.date >= s) & (rank_df["month"].dt.date <= e)]

rank_summary = (
    rank_df.groupby("lga", as_index=False)
    .agg(incident_count=("incident_count", "sum"), population_2024=("population_2024", "max"))
)
rank_summary["rate_per_100k"] = rank_summary["incident_count"] / rank_summary["population_2024"] * 100000
rank_summary = rank_summary.sort_values("rate_per_100k", ascending=False).head(top_n)

fig_rank = px.bar(
    rank_summary,
    x="rate_per_100k",
    y="lga",
    orientation="h",
    color="rate_per_100k",
    color_continuous_scale=COLOR_SCALE,
    title=f"Top {top_n} LGAs by crime rate per 100k",
    labels={"rate_per_100k": "Rate per 100k", "lga": "LGA"},
    hover_data={"incident_count": ":,", "rate_per_100k": ":.1f"}
)
fig_rank.update_layout(
    yaxis={"categoryorder": "total ascending"},
    coloraxis_showscale=False,
    height=max(400, top_n * 22)
)

st.plotly_chart(fig_rank, use_container_width=True)

# =========================
# Stacked area by category
# =========================
st.header("9. Crime Trend by Offence Category")

cat_trend = (
    filtered.groupby(["month", "offence_category"], as_index=False)["incident_count"]
    .sum()
    .sort_values("month")
)

fig_area = px.area(
    cat_trend,
    x="month",
    y="incident_count",
    color="offence_category",
    title=f"Monthly incidents by offence category — {lga_label}",
    labels={"month": "Month", "incident_count": "Incidents", "offence_category": "Category"}
)
fig_area.update_layout(hovermode="x unified", legend_title="Category")

st.plotly_chart(fig_area, use_container_width=True)

# =========================
# Year-over-year comparison
# =========================
st.header("10. Year-over-Year Comparison")

yoy_df = filtered.copy()
yoy_df["year"] = yoy_df["month"].dt.year.astype(str)
yoy_df["month_num"] = yoy_df["month"].dt.month

yoy_monthly = (
    yoy_df.groupby(["year", "month_num"], as_index=False)["incident_count"].sum()
)
yoy_monthly["month_name"] = yoy_monthly["month_num"].map(month_abbr)

fig_yoy = px.bar(
    yoy_monthly,
    x="month_name",
    y="incident_count",
    color="year",
    color_discrete_sequence=["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"],
    barmode="group",
    title=f"Incidents by month — year-over-year comparison ({lga_label})",
    labels={"month_name": "Month", "incident_count": "Incidents", "year": "Year"},
    category_orders={"month_name": list(month_abbr.values())}
)
fig_yoy.update_layout(hovermode="x unified", legend_title="Year")

st.plotly_chart(fig_yoy, use_container_width=True)

# =========================
# Month-over-month % change
# =========================
st.header("11. Crime Acceleration — Month-over-Month Change (%)")

mom = (
    filtered.groupby("month", as_index=False)["incident_count"]
    .sum()
    .sort_values("month")
)
mom["pct_change"] = mom["incident_count"].pct_change() * 100
mom_valid = mom.dropna(subset=["pct_change"]).copy()

fig_mom = px.bar(
    mom_valid,
    x="month",
    y="pct_change",
    color="pct_change",
    color_continuous_scale=COLOR_SCALE,
    title=f"Month-over-month % change in incidents — {lga_label}",
    labels={"month": "Month", "pct_change": "% change vs prior month"},
)
fig_mom.add_hline(y=0, line_dash="dash", line_color="gray", line_width=1)
fig_mom.update_layout(hovermode="x unified", coloraxis_showscale=False)

st.plotly_chart(fig_mom, use_container_width=True)

# =========================
# LGA summary table
# =========================
st.header("12. LGA Summary Table")

tbl_df = df.copy()
if selected_offence != "All":
    tbl_df = tbl_df[tbl_df["offence_category"] == selected_offence]
if isinstance(date_range, tuple) and len(date_range) == 2:
    s, e = date_range
    tbl_df = tbl_df[(tbl_df["month"].dt.date >= s) & (tbl_df["month"].dt.date <= e)]

tbl_summary = (
    tbl_df.groupby("lga", as_index=False)
    .agg(
        total_incidents=("incident_count", "sum"),
        population=("population_2024", "max")
    )
)
tbl_summary["rate_per_100k"] = (
    tbl_summary["total_incidents"] / tbl_summary["population"] * 100000
).round(1)

# YoY change per LGA
tbl_monthly = (
    tbl_df.groupby(["lga", "month"])["incident_count"].sum()
    .reset_index().sort_values(["lga", "month"])
)

def lga_yoy(grp):
    grp = grp.sort_values("month").reset_index(drop=True)
    if len(grp) < 13:
        return None
    last = grp.iloc[-1]["incident_count"]
    prev = grp.iloc[-13]["incident_count"]
    if prev == 0:
        return None
    return round((last - prev) / prev * 100, 1)

yoy_per_lga = (
    tbl_monthly.groupby("lga")[["month", "incident_count"]]
    .apply(lga_yoy)
    .reset_index()
    .rename(columns={0: "yoy_pct"})
)

tbl_sparklines = (
    tbl_monthly.groupby("lga")["incident_count"]
    .apply(make_sparkline)
    .reset_index()
    .rename(columns={"incident_count": "trend"})
)

tbl_summary = (
    tbl_summary
    .merge(yoy_per_lga, on="lga", how="left")
    .merge(tbl_sparklines, on="lga", how="left")
)

def trend_arrow(v):
    if pd.isna(v):
        return "—"
    if v > 5:
        return f"↑ {v:+.1f}%"
    if v < -5:
        return f"↓ {v:+.1f}%"
    return f"→ {v:+.1f}%"

tbl_summary["yoy_change"] = tbl_summary["yoy_pct"].apply(trend_arrow)
tbl_summary = tbl_summary.sort_values("rate_per_100k", ascending=False)

st.dataframe(
    tbl_summary[["lga", "total_incidents", "population", "rate_per_100k", "yoy_change", "trend"]]
    .rename(columns={
        "lga": "LGA",
        "total_incidents": "Total Incidents",
        "population": "Population",
        "rate_per_100k": "Rate per 100k",
        "yoy_change": "YoY Change",
        "trend": "Trend (8 months)"
    }),
    use_container_width=True,
    hide_index=True,
    height=420
)

# =========================
# Data preview & export
# =========================
with st.expander("Show filtered data"):
    st.dataframe(filtered.head(200))

csv_bytes = filtered.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Download filtered data as CSV",
    data=csv_bytes,
    file_name=f"nsw_crime_{lga_label.replace(' ', '_')}.csv",
    mime="text/csv"
)
