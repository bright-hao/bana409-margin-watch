from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, PercentFormatter
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Minghao Zhang | Margin Watch", page_icon="📊", layout="wide")

@st.cache_data
def load_data():
    data = pd.read_csv(Path(__file__).with_name("superstore.csv"), encoding="cp1252")
    data["Order Date"] = pd.to_datetime(data["Order Date"], format="%m/%d/%Y")
    return data


def money(value):
    return f"-${abs(value):,.0f}" if value < 0 else f"${value:,.0f}"


data = load_data()
st.title("Minghao Zhang · Margin Watch")
st.caption("For a regional sales manager deciding which product groups need a discount and cost review before next week's promotions.")
st.caption("Data: 03 Jan 2014 – 30 Dec 2017 · Kaggle snapshot · Production plan: refresh nightly; review every Monday.")

with st.sidebar:
    st.header("Your review")
    region = st.selectbox("Region", sorted(data["Region"].unique()), key="region")
    year = st.selectbox("Order year", sorted(data["Order Date"].dt.year.unique(), reverse=True), key="year")
    st.caption("Choose your region and a full calendar year. The snapshot is historical and does not refresh automatically.")
    st.divider()
    st.markdown("[Dataset and attribution](https://www.kaggle.com/datasets/vivek468/superstore-dataset-final)")

selected = data[(data["Region"] == region) & (data["Order Date"].dt.year == year)].copy()
if selected.empty:
    st.info("There are no order lines for this selection.")
    st.stop()

sales = selected["Sales"].sum()
profit = selected["Profit"].sum()
margin = profit / sales if sales else float("nan")
st.subheader(f"{region} · {year}")
left, middle, right = st.columns(3)
left.metric("Sales", money(sales), help="Sum of the source Sales column for selected order lines.")
middle.metric("Reported profit", money(profit), help="Sum of the source Profit column; the source does not specify all included costs.")
right.metric("Profit margin", f"{margin:.1%}", help="Total reported profit divided by total sales, not the average of line margins.")
st.caption(f"Scope: {len(selected):,} order lines from {selected['Order ID'].nunique():,} distinct orders. All dollars are treated as USD for this US retail example.")

by_category = selected.groupby("Sub-Category")["Profit"].sum().sort_values()
losses = by_category[by_category < 0]
if len(losses):
    names = ", ".join(losses.index[:3])
    tail = f" and {len(losses) - 3} more" if len(losses) > 3 else ""
    st.info(f"Review first: {names}{tail}. Together, the {len(losses)} loss-making product groups report {money(losses.sum())} profit. Inspect discounts and costs before changing promotions.")
else:
    st.info("No product group has negative total reported profit in this selection. Check the monthly trend for weaker periods before changing promotions.")

plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False, "axes.spines.left": False, "axes.edgecolor": "#D5DBDF", "text.color": "#243447", "axes.labelcolor": "#243447"})
trend_col, category_col = st.columns([1, 1.15], gap="large")
with trend_col:
    st.markdown("**When did margin weaken?**")
    monthly = selected.groupby(selected["Order Date"].dt.month)[["Sales", "Profit"]].sum().reindex(range(1, 13))
    monthly_margin = monthly["Profit"].div(monthly["Sales"])
    fig, ax = plt.subplots(figsize=(6.0, 4.1), layout="constrained")
    ax.plot(monthly.index, monthly_margin, color="#167D8D", linewidth=2.5, marker="o", markersize=4)
    ax.axhline(0.10, color="#BE6A42", linestyle="--", linewidth=1.2, label="10% review trigger")
    ax.axhline(0, color="#7A8793", linewidth=0.8)
    ax.set_xticks(range(1, 13), ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"])
    ax.set_xlabel(f"Order month · {year}")
    ax.yaxis.set_major_formatter(PercentFormatter(1, decimals=0))
    ax.set_ylabel("Reported profit / sales")
    ax.grid(axis="y", alpha=0.15)
    ax.legend(frameon=False, loc="best", fontsize=9)
    st.pyplot(fig)
    plt.close(fig)
    st.caption("The 10% line is a proposed review trigger, not a validated company target. A missing month would appear as a gap, not zero profit.")
with category_col:
    st.markdown("**Which product groups need attention?**")
    fig, ax = plt.subplots(figsize=(6.8, 4.1), layout="constrained")
    ax.barh(by_category.index, by_category.values, color=["#C76D55" if x < 0 else "#167D8D" for x in by_category.values], height=0.7)
    ax.axvline(0, color="#7A8793", linewidth=0.8)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, pos: f"-${abs(x)/1000:.0f}k" if x < 0 else f"${x/1000:.0f}k"))
    ax.set_xlabel("Total reported profit · USD")
    ax.tick_params(axis="y", length=0, labelsize=9)
    ax.grid(axis="x", alpha=0.15)
    st.pyplot(fig)
    plt.close(fig)
    st.caption("Coral bars show a loss. All product groups remain visible so a large loss cannot disappear from a top-five ranking.")

with st.expander("How to read this review"):
    st.write("Use monthly margin to identify a weak period, then review product groups with negative total profit. In production, inspect the latest completed month's margin each Monday; below 10% triggers a review, not an automatic price change.")
    st.write("This is a sample retail dataset, not a verified company's live accounts. Its public metadata does not establish transaction authenticity or define every cost in Profit. Results describe this file only. Order lines are not separate orders, and large transactions can move the totals. Discounts and losses can be associated without proving that discounts caused the losses.")
    st.write("No inventory, returns, price history, marketing spending, or full cost ledger is available. This dashboard cannot set optimal prices or calculate complete business net income.")
