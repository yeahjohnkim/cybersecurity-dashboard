"""
Project: Global Cybersecurity Threats Explorer Dashboard 2015~2024
Author: John Kim
Created: 2025/05
Description: An interactive Streamlit dashboard analyzing cyberattack losses, attack types, 
            industries, and defense effectiveness.

Data Source: "Global_Cybersecurity_Threats_2015-2024.xlsx”
Original Source: Atharva Soundankar
https://www.kaggle.com/datasets/atharvasoundankar/global-cybersecurity-threats-2015-2024/data

Usage in Terminal: 
    1) pip install -r requirements.txt
    2) streamlit run main_v2.py
"""

# ─────────────────────────────────────────────────────────────────────────────

import io
import requests

import pandas as pd
import plotly.express as px
import streamlit as st


# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION

DATA_URL  = "https://raw.githubusercontent.com/yeahjohnkim/home/main/Global_Cybersecurity_Threats_2015-2024.xlsx"
CACHE_TTL = 3600

@st.cache_data(ttl=CACHE_TTL)
def load_data(url: str) -> pd.DataFrame:
    resp = requests.get(url)
    resp.raise_for_status()
    return pd.read_excel(io.BytesIO(resp.content))

# ─────────────────────────────────────────────────────────────────────────────
# APP SETUP

st.set_page_config(
    page_title="Global Cybersecurity Threats Explorer",
    layout="wide",
)

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR FILTERS

def sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.header("Filters")

    year_range = st.sidebar.slider(
        "Select Year Range",
        int(df.Year.min()),
        int(df.Year.max()),
        (int(df.Year.min()), int(df.Year.max())),
    )
    countries = st.sidebar.multiselect(
        "Select Countries",
        options=sorted(df.Country.unique()),
        default=[df.Country.mode()[0]],
    )

    return df[df.Year.between(*year_range) & df.Country.isin(countries)]

# ─────────────────────────────────────────────────────────────────────────────
# PLOTTING FUNCTIONS

def plot_loss_by_country(subset: pd.DataFrame):
    loss = (
        subset
        .groupby("Country")["Financial Loss (in Million $)"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )
    fig = px.bar(
        loss,
        x="Financial Loss (in Million $)",
        y="Country",
        orientation="h",
        title="Total Financial Loss by Country",
        color="Country",
        height=600,
    )
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    return fig


def plot_avg_loss_by_attack(subset: pd.DataFrame):
    avg_atk = (
        subset
        .groupby("Attack Type")["Financial Loss (in Million $)"]
        .mean()
        .reset_index()
    )
    return px.pie(
        avg_atk,
        values="Financial Loss (in Million $)",
        names="Attack Type",
        title="Average Loss by Attack Type",
        height=500,
    )


def plot_top_country_industry(subset: pd.DataFrame):
    combo = (
        subset
        .groupby(["Country","Target Industry"])["Financial Loss (in Million $)"]
        .mean()
        .nlargest(10)
        .reset_index()
    )
    combo["Label"] = combo.Country + " – " + combo["Target Industry"]
    fig = px.bar(
        combo,
        x="Financial Loss (in Million $)",
        y="Label",
        orientation="h",
        color="Target Industry",
        title="Top 10 Country-Industry Cyber Losses",
        height=600,
    )
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    return fig


def plot_resolution_heatmap(subset: pd.DataFrame):
    rt = (
        subset
        .groupby(["Security Vulnerability Type","Defense Mechanism Used"])
        ["Incident Resolution Time (in Hours)"]
        .mean()
        .reset_index()
    )
    heat = rt.pivot(
        index="Security Vulnerability Type",
        columns="Defense Mechanism Used",
        values="Incident Resolution Time (in Hours)"
    )
    return px.imshow(
        heat,
        text_auto=".1f",
        color_continuous_scale="RdBu_r",
        title="Avg Resolution Time (hrs): Vulnerability vs Defense",
        aspect="auto",
        height=600,
    )

# ─────────────────────────────────────────────────────────────────────────────
# MAIN APPLICATION

def main():
    df = load_data(DATA_URL)
    subset = sidebar_filters(df)

    st.title("Global Cybersecurity Threats Explorer")
    tabs = st.tabs([
        "By Country",
        "By Attack Type",
        "Industry/Country",
        "Resolution Heatmap",
    ])

    with tabs[0]:
        st.plotly_chart(plot_loss_by_country(subset), use_container_width=True)

    with tabs[1]:
        st.plotly_chart(plot_avg_loss_by_attack(subset), use_container_width=True)

    with tabs[2]:
        st.plotly_chart(plot_top_country_industry(subset), use_container_width=True)

    with tabs[3]:
        st.plotly_chart(plot_resolution_heatmap(subset), use_container_width=True)


if __name__ == "__main__":
    main()
