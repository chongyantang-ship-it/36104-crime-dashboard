# NSW Crime Pressure Dashboard

Streamlit dashboard prototype for UTS 36104 Data Visualisation and Narratives Assignment 3.

## Project Purpose

This dashboard explores the question:

**Where is crime pressure rising across NSW, what offence types are driving the change, and where should prevention resources be prioritised next?**

The intended stakeholders are local council community safety planners and related community service providers.

The dashboard follows a **What → So What → What Next** narrative structure:

- **What:** Where is crime pressure concentrated across NSW?
- **So What:** What offence types, trends, and socioeconomic conditions help explain the pattern?
- **What Next:** Which LGAs may require closer attention or prevention planning?

## Data Sources

### Main dataset

- NSW recorded crime data by offence, LGA, subcategory, and month.
- Cleaned from wide format into long format with the fields:
  - `lga`
  - `offence_category`
  - `subcategory`
  - `month`
  - `incident_count`

### Population supporting dataset

- ABS 2024 LGA population data.
- Joined to the crime dataset by LGA name.
- Added fields:
  - `population_2024`
  - `rate_per_100k`

The population-adjusted crime rate allows fairer comparison between LGAs with different population sizes.

### Spatial boundary dataset

- NSW LGA boundary data converted into a simplified GeoJSON file.
- Used to create the NSW LGA hotspot map.
- File used:
  - `geo/lga_nsw_2024_simplified.geojson`

### Socioeconomic enrichment dataset

- 2021 ABS Census General Community Profile data at LGA level.
- Selected indicators joined to the crime dataset through LGA code/name:
  - median household income per week
  - median rent per week
  - median mortgage repayment per month
  - average household size

This enrichment helps the dashboard move beyond identifying **where** crime pressure is concentrated. It supports the **“So What”** part of the narrative by showing whether high-crime LGAs also have different income or housing-cost conditions.

## Current Features

- NSW LGA hotspot map showing population-adjusted crime pressure by rate per 100,000 people
- LGA filter, including multi-LGA selection
- Offence category filter
- Date range filter
- KPI summary cards:
  - total incidents
  - latest month incidents
  - 12-month change
  - crime rate per 100,000 people
  - top offence driver
- Monthly trend chart
- Interactive trend metric toggle:
  - incident count
  - rate per 100,000 people
- Offence composition chart
- Selected area insight panel
- Seasonality heatmap
- Side-by-side LGA comparison
- LGA ranking by crime rate
- Crime trend by offence category
- Year-over-year comparison
- Month-over-month change chart
- LGA summary table
- Socioeconomic context section comparing crime rate with selected 2021 Census indicators
- Filtered data preview and CSV export

## Advanced Feature Progress

This prototype currently supports:

1. **Context-aware filtering**  
   The dashboard updates based on selected LGA, offence category, date range, and trend metric.

2. **Population-adjusted comparison**  
   Crime pressure can be viewed as raw incident count or rate per 100,000 people.

3. **Spatial hotspot map**  
   The dashboard uses NSW LGA boundary data to show where crime pressure is concentrated geographically.

4. **Rich map tooltips**  
   The hotspot map includes additional information such as total incidents, population, rate per 100k, top offence, and recent trend.

5. **Socioeconomic context / enriched dataset**  
   The dashboard joins crime data with ABS Census indicators to support deeper **“So What”** analysis beyond a single crime CSV.

6. **Narrative structure**  
   The dashboard follows a **What → So What → What Next** flow to support stakeholder decision-making.

Planned improvements include clearer recommendation logic, stronger explanation of socioeconomic patterns, and a more polished presentation layout.

## How to Run Locally

Install dependencies:

`python -m pip install -r requirements.txt`

Run the app:

`python -m streamlit run app.py`

## Files

- `app.py` — Streamlit dashboard prototype
- `crime_long_2024_onwards.csv` — cleaned crime dataset in long format
- `crime_with_population_2024_onwards.csv` — crime dataset enriched with ABS 2024 LGA population
- `crime_with_population_socioeconomic_2024_onwards.csv` — crime dataset enriched with population and 2021 Census socioeconomic indicators
- `geo/lga_nsw_2024_simplified.geojson` — simplified NSW LGA boundary file for the hotspot map
- `requirements.txt` — required Python packages

## Technical Contribution

This version includes:

- Cleaning the NSW crime dataset into long format
- Joining ABS 2024 LGA population data
- Calculating crime rate per 100,000 people
- Creating the NSW LGA hotspot map
- Adding interactive filters and trend metric toggle
- Adding socioeconomic enrichment using 2021 Census indicators
- Adding a socioeconomic context visualisation
- Maintaining GitHub version control
- Deploying the dashboard prototype through Streamlit Cloud

## Notes

The socioeconomic context section is exploratory. It does not prove causation between income, housing cost, and crime. Instead, it helps stakeholders identify patterns that may require deeper local investigation.
