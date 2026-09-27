import pandas as pd
import plotly.express as px
import streamlit as st

# ----------------------------------------------------------------------
# Page setup
# ----------------------------------------------------------------------
st.set_page_config(page_title="Lebanon Tourism Explorer", layout="wide")

# ----------------------------------------------------------------------
# Load & clean data
# ----------------------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("Tourism_Lebanon_2023.csv")

    # refArea is a long dbpedia/linked-data URL, e.g.
    # "https://dbpedia.org/page/Mount_Lebanon_Governorate"
    # we only want the readable name at the end of it
    def clean_region(url):
        name = url.rstrip("/").split("/")[-1]
        name = name.replace("_", " ")
        name = name.replace(",_Lebanon", "").replace(", Lebanon", "")
        name = name.replace("%27", "'")
        # Some names (e.g. "Zahlé", "Minyeh-Danniyeh") were double-encoded as
        # UTF-8 somewhere upstream, producing mojibake like "ZahlÃ©". Undo it
        # where possible; if a name was never double-encoded, this is a no-op.
        try:
            name = name.encode("latin1").decode("utf8")
        except (UnicodeDecodeError, UnicodeEncodeError):
            pass
        return name

    df["Region"] = df["refArea"].apply(clean_region)
    df["Town"] = df["Town"].str.strip()
    return df

df = load_data()

# ----------------------------------------------------------------------
# Header & context
# ----------------------------------------------------------------------
st.title("🇱🇧 Lebanon Tourism Explorer")

st.markdown(
    """
This page explores the **Tourism Lebanon 2023** dataset (Impact Open Data /
AUB CODEC), which records tourism infrastructure for **1,137 towns** across
Lebanon's 25 regions (governorates and districts). For every town, the
dataset tracks the number of **hotels, restaurants, cafes, and guest
houses**, along with a **Tourism Index** (0–10) that summarizes how
tourism-ready the town is.
"""
)

col1, col2 = st.columns(2)
with col1:
    st.metric("Towns in dataset", f"{df.shape[0]:,}")
    st.metric("Regions covered", df["Region"].nunique())
with col2:
    corr = df["Total number of restaurants"].corr(df["Total number of cafes"])
    st.metric("Restaurants–cafes correlation", f"{corr:.2f}")
    top5_share = (
        df.groupby("Region")["Total number of hotels"].sum().sort_values(ascending=False).head(5).sum()
        / df["Total number of hotels"].sum()
    )
    st.metric("Hotel share held by top 5 regions", f"{top5_share:.0%}")

st.info(
    "**Two things worth noticing across the whole dataset:** "
    "(1) restaurants and cafes tend to grow together in the same town "
    "(correlation ≈ 0.73) — tourism amenities cluster rather than spread "
    "evenly; and (2) just 5 of Lebanon's 25 regions hold over 40% of all "
    "hotels, showing tourism infrastructure is heavily concentrated."
)

st.divider()

# ----------------------------------------------------------------------
# Linked interaction widgets
# ----------------------------------------------------------------------
st.subheader("Explore a region")

region_list = sorted(df["Region"].unique())
selected_region = st.selectbox(
    "1. Choose a region",
    options=region_list,
    index=region_list.index("Mount Lebanon Governorate") if "Mount Lebanon Governorate" in region_list else 0,
)

region_df = df[df["Region"] == selected_region].copy()

# Town options depend on the region chosen above (drill-down link)
town_options = sorted(region_df["Town"].unique())
default_towns = (
    region_df.sort_values("Tourism Index", ascending=False)["Town"].head(3).tolist()
)
selected_towns = st.multiselect(
    "2. Highlight specific towns in this region",
    options=town_options,
    default=default_towns,
)

with st.expander("Why these two controls? (design justification)"):
    st.markdown(
        """
**Region selector — which question it answers:**
"Which regions have strong or weak tourism infrastructure, and how does a
town in this region compare to others nearby?" A dropdown (`st.selectbox`)
was used instead of a multiselect or slider because a region is a single,
unordered category the user should focus on one at a time — showing all 25
regions superimposed would add clutter without adding insight. This
reflects the *"overview first, zoom and filter"* idea from the visual
information-seeking mantra: the metrics above give the overview, and this
control lets the reader zoom into one part of it.

**Town multiselect — which question it answers:**
"Within this region, which specific towns stand out, and how do they
compare to each other on restaurants vs. cafes?" A multiselect was chosen
over a single dropdown because the reader may want to compare zero, one, or
several towns at once across both charts below. Its option list is **built
from the region selected above**, not from all 1,137 towns — this is the
required drill-down link: choosing a region first narrows and changes what
can be picked next, rather than the two controls filtering independently.
This reflects the *focus + context* idea: selected towns are highlighted
in color while the rest of the region is still shown, greyed out, as
context — reducing clutter while keeping the reader oriented.
"""
    )

if region_df.empty:
    st.warning("No towns found for this region.")
    st.stop()

# ----------------------------------------------------------------------
# Visualization 1: Bar chart — Tourism Index by town in the region
# ----------------------------------------------------------------------
st.subheader(f"Tourism Index by town — {selected_region}")

bar_df = region_df.sort_values("Tourism Index", ascending=False).copy()
bar_df["Highlighted"] = bar_df["Town"].apply(
    lambda t: "Selected" if t in selected_towns else "Other towns"
)

fig_bar = px.bar(
    bar_df,
    x="Town",
    y="Tourism Index",
    color="Highlighted",
    color_discrete_map={"Selected": "#1C7293", "Other towns": "#D9D9D9"},
    title=f"Tourism Index for every town in {selected_region}",
)
fig_bar.update_layout(xaxis_tickangle=-45, showlegend=True)
st.plotly_chart(fig_bar, use_container_width=True)

if selected_towns:
    avg_selected = bar_df[bar_df["Town"].isin(selected_towns)]["Tourism Index"].mean()
    avg_region = bar_df["Tourism Index"].mean()
    st.caption(
        f"Selected towns average a Tourism Index of **{avg_selected:.1f}**, "
        f"versus **{avg_region:.1f}** for {selected_region} as a whole."
    )

# ----------------------------------------------------------------------
# Visualization 2: Scatter — restaurants vs cafes in the region
# ----------------------------------------------------------------------
st.subheader(f"Restaurants vs. cafes — {selected_region}")

scatter_df = region_df.copy()
scatter_df["Highlighted"] = scatter_df["Town"].apply(
    lambda t: "Selected" if t in selected_towns else "Other towns"
)

fig_scatter = px.scatter(
    scatter_df,
    x="Total number of restaurants",
    y="Total number of cafes",
    color="Highlighted",
    color_discrete_map={"Selected": "#D9534F", "Other towns": "#B8C4CE"},
    size=scatter_df["Highlighted"].map({"Selected": 14, "Other towns": 8}),
    hover_name="Town",
    title=f"Restaurants vs. cafes for towns in {selected_region}",
)
st.plotly_chart(fig_scatter, use_container_width=True)

st.caption(
    "Points are sized and colored by whether the town is in your selection "
    "above — the rest of the region stays visible as context."
)

st.divider()
st.caption(
    "Data source: Tourism Lebanon 2023, Impact Open Data / AUB CODEC "
    "linked dataset."
)