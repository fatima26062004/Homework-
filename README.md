# Lebanon Tourism Explorer

An interactive Streamlit app exploring the **Tourism Lebanon 2023** dataset
(Impact Open Data / AUB CODEC) — 1,137 towns across 25 Lebanese regions,
with hotel, restaurant, cafe, guest house counts and a 0–10 Tourism Index.

## What it does

- Gives context on the dataset and surfaces two headline insights
  (restaurant/cafe clustering, and hotel concentration in a handful of
  regions).
- Two **linked** interactive controls:
  1. A **region dropdown** — pick one of Lebanon's 25 regions.
  2. A **town multiselect** — its list of options is built from the region
     chosen above, so picking a region narrows what can be selected next
     (drill-down, not two independent filters).
- Two Plotly charts that respond to both controls:
  - A bar chart of Tourism Index by town in the selected region, with
    selected towns highlighted.
  - A scatter plot of restaurants vs. cafes for towns in the selected
    region, with selected towns highlighted.
- An in-page expander explaining the design reasoning behind each control.

## Running locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Files

- `app.py` — the Streamlit app
- `Tourism_Lebanon_2023.csv` — the dataset
- `requirements.txt` — Python dependencies for Streamlit Community Cloud

## Data source

Tourism Lebanon 2023, Impact Open Data / AUB CODEC linked dataset.
https://linked.aub.edu.lb:8502/PKGCubes_Explorer
