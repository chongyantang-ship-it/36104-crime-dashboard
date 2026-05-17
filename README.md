# NSW Crime Pressure Dashboard

An interactive Streamlit dashboard for UTS 36104 Data Visualisation and Narratives Assignment 3.

---

## Project Overview

This project transforms multi-dimensional NSW crime data into an interactive, stakeholder-focused narrative dashboard. Rather than functioning as a simple status dashboard, it is designed as a decision-support tool to help users identify where crime pressure is rising, what offence patterns are driving that pressure, and which Local Government Areas (LGAs) may require closer prevention-focused attention.

### Narrative Question

**Where is crime pressure rising across NSW, what offence types are driving the change, and where should prevention resources be prioritised next?**

### Primary Stakeholder

Local council community safety planners and related community service providers in NSW.

---

## User Persona and User Story

### User Persona

A community safety planner working within a NSW local council who needs evidence to compare local crime pressure with the NSW baseline, identify changing offence patterns, and support prevention-focused planning or funding requests.

### User Story

**As a** local community safety planner,  
**I want to** compare crime pressure across NSW LGAs, examine offence trends and composition, and interpret local patterns using supporting context,  
**so that** I can identify higher-priority areas for targeted prevention and community safety planning.

### Acceptance Criteria

The dashboard should allow the stakeholder to:

- identify LGAs with relatively high crime pressure
- compare selected LGAs against the NSW baseline
- interpret crime trends over time
- examine offence composition and drivers
- view population-adjusted rates rather than relying only on raw counts
- use supporting contextual indicators to inform prioritisation

### Definition of Done

The dashboard is considered complete when it enables a stakeholder to move from overview to investigation and then to prioritisation using an interpretable What → So What → What Next flow.

---

## Narrative Arc

This dashboard follows a **What → So What → What Next** narrative structure.

- **What:** Where is crime pressure concentrated across NSW?
- **So What:** What offence types, trend patterns, and contextual indicators help explain those differences?
- **What Next:** Which LGAs may require closer monitoring, targeted prevention, or community safety planning?

This arc was chosen because it supports executive-style decision-making and helps stakeholders move from broad pattern recognition to local action.

---

## Data Sources

### 1. Main dataset - Crime Data

- NSW recorded crime data by offence, LGA, subcategory, and month.
- Cleaned from wide format into long format with the fields:
  - `lga`
  - `offence_category`
  - `subcategory`
  - `month`
  - `incident_count`

### 2. Supporting Dataset - ABS Population

- ABS 2024 LGA population data.
- Joined to the crime dataset by LGA name.
- Added fields:
  - `population_2024`
  - `rate_per_100k`

This enables fairer comparison between LGAs of different population sizes.

### 3. Supporting Dataset - Spatial boundary dataset

- NSW LGA boundary data converted into a simplified GeoJSON file.
- Used to create the NSW LGA hotspot map.
- File used:
  - `geo/lga_nsw_2024_simplified.geojson`

### 4. Supporting Dataset - Socioeconomic Enrichment Dataset

- 2021 ABS Census General Community Profile data at LGA level.
- Selected indicators joined to the crime dataset through LGA code/name:
  - `median household income per week`
  - `median rent per week`
  - `median mortgage repayment per month`
  - `average household size`

This enrichment helps the dashboard move beyond identifying **where** crime pressure is concentrated and supports the **“So What”** part of the narrative by showing whether high-crime LGAs also have different income or housing-cost conditions.

---

## Data Dictionary

| Variable | Type | Description | Provenance |
|---|---|---|---|
| `lga` | string | Local Government Area name | NSW crime dataset |
| `offence_category` | string | High-level offence category | NSW crime dataset |
| `subcategory` | string | Offence subcategory | NSW crime dataset |
| `month` | date/string | Reporting month | NSW crime dataset |
| `incident_count` | integer | Number of recorded incidents | NSW crime dataset |
| `population_2024` | integer | 2024 estimated LGA population | ABS population dataset |
| `rate_per_100k` | float | Crime incidents per 100,000 population | Calculated by team |
| `median_household_income_weekly` | numeric | Median weekly household income | ABS Census |
| `median_rent_weekly` | numeric | Median weekly rent | ABS Census |
| `median_mortgage_monthly` | numeric | Median monthly mortgage repayment | ABS Census |
| `average_household_size` | numeric | Average household size | ABS Census |

---

## Implemented Advanced Features

### 1. Context-Aware Filtering

Selections made through the LGA filter, offence category filter, date range filter, and trend metric toggle update multiple visuals and summary outputs dynamically.

### 2. Rich Visual Tooltips

The hotspot map provides extended contextual detail including:

- total incidents
- population
- rate per 100,000
- top offence driver
- recent trend signal

### 3. Narrative Scrollytelling

The dashboard is structured as a guided sequence of narrative sections rather than a flat dashboard, helping the user move from overall pattern recognition to detailed comparison and prioritisation.

### Additional Analytical Enrichment

The dashboard combines crime data with ABS population and ABS Census contextual indicators to support a deeper “So What” analysis beyond a single CSV source.

---

## Dashboard Features

Current dashboard features include:

- NSW LGA hotspot map showing population-adjusted crime pressure
- LGA filter, including multi-LGA selection
- offence category filter
- date range filter
- KPI summary cards:
  - total incidents
  - latest month incidents
  - 12-month change
  - crime rate per 100,000 people
  - top offence driver
- monthly trend chart
- trend metric toggle:
  - incident count
  - rate per 100,000 people
- offence composition chart
- selected area insight panel
- seasonality heatmap
- side-by-side LGA comparison
- LGA ranking by crime rate
- crime trend by offence category
- year-over-year comparison
- month-over-month change chart
- LGA summary table
- socioeconomic context section
- filtered data preview and CSV export

---

## Design System and Accessibility

The dashboard follows a consistent visual system across maps, charts, cards, filters, and tables.

### Design choices

- consistent colour palette across all visuals
- repeated section hierarchy following the narrative arc
- card-based layout for readability
- population-adjusted comparison as a fairness lens
- descriptive chart titles and section headers

### Accessibility considerations

- high contrast text and interface elements
- readable chart labels and clear headings
- filters grouped logically for intuitive use
- avoidance of colour-only meaning where possible
- consistent interaction patterns across charts and tables

---

## Repository Structure

- `app.py` — main Streamlit application
- `crime_long_2024_onwards.csv` — cleaned long-format crime dataset
- `crime_with_population_2024_onwards.csv` — crime dataset enriched with ABS population
- `crime_with_population_socioeconomic_2024_onwards.csv` — crime dataset enriched with population and Census indicators
- `geo/lga_nsw_2024_simplified.geojson` — simplified NSW LGA boundary file
- `requirements.txt` — required Python packages

---

## Code Logic Overview

The application follows this workflow:

1. load cleaned crime and supporting datasets
2. merge population and socioeconomic indicators
3. calculate population-adjusted rates
4. apply user-selected filters dynamically
5. update map, KPI cards, trends, comparisons, and summary outputs
6. support stakeholder interpretation through the What → So What → What Next narrative flow

---

## How to Run Locally

Install dependencies:

`python -m pip install -r requirements.txt`

Run the app:

`python -m streamlit run app.py`

---

## Credits

### Team Members

- Jiayu Hao - Integration Lead: coordinate timeline, workflow planing, ensures smooth handovers between roles.
- Diego Zuniga - Data Lead: data selection and validation, adjust Streamlit.
- Chongyan Tang - Technical Lead: Streamlit implementation and deployment.
- Yogesh Sajith Kumar - Narrative Lead: Narrative lead, stakeholder framing and storytelling.
- Muthu Kumaran Chandrasekar Jayanthi — Design/UX lead: layout and interface direction, help decide stakeholder.
- Sushant Bhattarai — Presentation/communication lead: pitch delivery and script refinement
- Ce Wang — Document/QA lead: README refinement and quality checking

### Data Sources 
**TODO:**
- NSW crime dataset / BOCSAR source
- ABS 2024 LGA population data
- ABS Census General Community Profile data
- NSW LGA boundary data

**Population and Census indicators were joined to the crime dataset using matched LGA names / codes after standardising naming conventions across files.**

### Tools and Platforms
- Python
- Streamlit
- Pandas
- Plotly
- GeoPandas / GeoJSON workflow
- GitHub
- Streamlit Community Cloud

## Limitations
- The socioeconomic context section is exploratory and does not imply causation.
- The dashboard is designed to support prioritisation and interpretation, not causal inference or operational policing.
- Some contextual indicators are limited to currently available ABS/Census variables.
- Results should be interpreted as evidence for further local investigation rather than as standalone policy conclusions.