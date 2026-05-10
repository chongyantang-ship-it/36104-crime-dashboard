  # NSW Crime Pressure Dashboard

Streamlit dashboard prototype for UTS 36104 Data Visualisation and Narratives Assignment 3.

## Project Purpose

This dashboard explores the question:

**Where is crime pressure rising across NSW, what offence types are driving the change, and where should prevention resources be prioritised next?**

The intended stakeholders are local council community safety planners and related community service providers.

## Data Sources

### Main dataset
- NSW recorded crime data by offence, LGA and month.
- Cleaned into long format with the fields:
  - `lga`
  - `offence_category`
  - `subcategory`
  - `month`
  - `incident_count`

### Supporting dataset
- ABS 2024 LGA population data.
- Joined to the crime dataset by LGA name.
- Added fields:
  - `population_2024`
  - `rate_per_100k`

The population-adjusted rate allows fairer comparison between LGAs with different population sizes.

### Socioeconomic enrichment dataset

- 2021 ABS Census General Community Profile data at LGA level.
- Selected indicators joined to the crime dataset through LGA code/name:
  - median household income per week
  - median rent per week
  - median mortgage repayment per month
  - average household size

This enrichment helps the dashboard move beyond identifying where crime pressure is concentrated and supports the “So What” part of the narrative by showing whether high-crime LGAs also have different income or housing-cost conditions.

## Current Features

- NSW LGA hotspot map showing population-adjusted crime pressure by rate per 100,000 people
- LGA filter
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
- Socioeconomic context section comparing crime rate with selected 2021 Census indicators
- Data preview table

## Advanced Feature Progress

This prototype currently supports:

1. **Context-aware filtering**  
   The dashboard updates based on selected LGA, offence category, date range and trend metric.

2. **Population-adjusted comparison**  
   Crime pressure can be viewed as raw incident count or rate per 100,000 people.

3. **Narrative structure**  
   The dashboard follows a What → So What → What Next narrative flow.

4. **Spatial hotspot map**  
   The dashboard uses NSW LGA boundary data to show where crime pressure is concentrated geographically.

5. **Socioeconomic context / enriched dataset**
   The dashboard joins crime data with ABS Census indicators to support deeper “So What” analysis beyond a single crime CSV.

Planned improvements include richer tooltips, clearer recommendation logic, and stronger explanation of socioeconomic patterns.

## How to Run Locally

Install dependencies:

```bash
python -m pip install -r requirements.txt
