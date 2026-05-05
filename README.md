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

## Current Features

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
- Data preview table

## Advanced Feature Progress

This prototype currently supports:

1. **Context-aware filtering**  
   The dashboard updates based on selected LGA, offence category, date range and trend metric.

2. **Population-adjusted comparison**  
   Crime pressure can be viewed as raw incident count or rate per 100,000 people.

3. **Narrative structure**  
   The dashboard follows a What → So What → What Next narrative flow.

Planned improvements include richer tooltips, map-based hotspot view, and stronger recommendation logic.

## How to Run Locally

Install dependencies:

```bash
python -m pip install -r requirements.txt
