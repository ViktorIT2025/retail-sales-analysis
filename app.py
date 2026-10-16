"""Retail Sales Dashboard.

Run from the repo folder with:  streamlit run app.py
"""
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Retail Sales Dashboard", layout="wide")

# Fixed colors per category, so a category keeps its color in every chart
CATEGORY_COLORS = {"Electronics": "#2a78d6", "Clothing": "#eb6834", "Beauty": "#1baf7a"}
MAIN_COLOR = "#2a78d6"
AGE_BINS = [17, 25, 35, 45, 55, 64]
AGE_LABELS = ["18-25", "26-35", "36-45", "46-55", "56-64"]
DAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


@st.cache_data  # load the CSV once, not on every click
def load_data():
    df = pd.read_csv("retail_sales_dataset.csv", parse_dates=["Date"])
    df["Age Group"] = pd.cut(df["Age"], bins=AGE_BINS, labels=AGE_LABELS).astype(str)
    df["Month"] = df["Date"].dt.to_period("M").dt.to_timestamp()
    df["Weekday"] = df["Date"].dt.day_name()
    return df


def style(fig, y_title):
    """Shared chart look: no chart border, light grid, readable hover."""
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        yaxis_title=y_title,
        xaxis_title=None,
        legend_title=None,
        hovermode="closest",
    )
    fig.update_yaxes(gridcolor="rgba(128,128,128,0.2)")
    return fig


df = load_data()

# ---------- Filters (sidebar) ----------
st.sidebar.header("Filters")
min_date, max_date = df["Date"].min().date(), df["Date"].max().date()
date_range = st.sidebar.date_input("Dates", (min_date, max_date), min_value=min_date, max_value=max_date)
categories = st.sidebar.multiselect("Product category", list(CATEGORY_COLORS), default=list(CATEGORY_COLORS))
genders = st.sidebar.multiselect("Gender", sorted(df["Gender"].unique()), default=sorted(df["Gender"].unique()))
age_min, age_max = st.sidebar.slider("Age", int(df["Age"].min()), int(df["Age"].max()),
                                     (int(df["Age"].min()), int(df["Age"].max())))

# The date picker returns one date while the user is still choosing the second
start, end = (date_range if len(date_range) == 2 else (date_range[0], max_date))

filtered = df[
    df["Date"].dt.date.between(start, end)
    & df["Product Category"].isin(categories)
    & df["Gender"].isin(genders)
    & df["Age"].between(age_min, age_max)
]

# ---------- Header and KPIs ----------
st.title("Retail Sales Dashboard")
st.caption("1,000 transactions from a Kaggle retail dataset, Jan 2023 to Jan 2024. Use the filters on the left.")

if filtered.empty:
    st.warning("No sales match these filters.")
    st.stop()

k1, k2, k3, k4 = st.columns(4)
k1.metric("Revenue", f"{filtered['Total Amount'].sum():,.0f}")
k2.metric("Transactions", f"{len(filtered):,}")
k3.metric("Avg transaction", f"{filtered['Total Amount'].mean():,.0f}")
k4.metric("Units sold", f"{filtered['Quantity'].sum():,}")

overview, customers, data_tab = st.tabs(["Sales overview", "Customers", "Data"])

# ---------- Tab 1: Sales overview ----------
with overview:
    left, right = st.columns(2)

    # Only full months of 2023; January 2024 has just one day of data
    monthly = (filtered[filtered["Date"].dt.year == 2023]
               .groupby("Month", as_index=False)["Total Amount"].sum())
    fig = px.line(monthly, x="Month", y="Total Amount", markers=True, color_discrete_sequence=[MAIN_COLOR])
    fig.update_traces(line_width=2, marker_size=8, hovertemplate="%{x|%b %Y}<br>Revenue: %{y:,.0f}<extra></extra>")
    left.subheader("Monthly revenue, 2023")
    left.plotly_chart(style(fig, "Revenue"), use_container_width=True)

    by_cat = (filtered.groupby("Product Category", as_index=False)["Total Amount"].sum()
              .sort_values("Total Amount", ascending=False))
    fig = px.bar(by_cat, x="Product Category", y="Total Amount", color="Product Category",
                 color_discrete_map=CATEGORY_COLORS, text_auto=",.0f")
    fig.update_traces(hovertemplate="%{x}<br>Revenue: %{y:,.0f}<extra></extra>")
    fig.update_layout(showlegend=False)
    right.subheader("Revenue by category")
    right.plotly_chart(style(fig, "Revenue"), use_container_width=True)

    by_day = (filtered.groupby("Weekday")["Total Amount"].sum()
              .reindex(DAY_ORDER, fill_value=0).reset_index())
    fig = px.bar(by_day, x="Weekday", y="Total Amount", color_discrete_sequence=[MAIN_COLOR], text_auto=",.0f")
    fig.update_traces(hovertemplate="%{x}<br>Revenue: %{y:,.0f}<extra></extra>")
    st.subheader("Revenue by day of the week")
    st.plotly_chart(style(fig, "Revenue"), use_container_width=True)

# ---------- Tab 2: Customers ----------
with customers:
    left, right = st.columns(2)

    by_age = (filtered.groupby("Age Group")["Total Amount"].mean()
              .reindex(AGE_LABELS).dropna().reset_index())
    fig = px.bar(by_age, x="Age Group", y="Total Amount", color_discrete_sequence=[MAIN_COLOR], text_auto=",.0f")
    fig.update_traces(hovertemplate="Age %{x}<br>Avg spend: %{y:,.0f}<extra></extra>")
    left.subheader("Average spend by age group")
    left.plotly_chart(style(fig, "Average spend"), use_container_width=True)

    by_gender = filtered.groupby(["Gender", "Product Category"], as_index=False)["Total Amount"].sum()
    fig = px.bar(by_gender, x="Gender", y="Total Amount", color="Product Category", barmode="group",
                 color_discrete_map=CATEGORY_COLORS, category_orders={"Product Category": list(CATEGORY_COLORS)})
    fig.update_traces(hovertemplate="%{x}<br>Revenue: %{y:,.0f}<extra></extra>")
    right.subheader("Revenue by gender and category")
    right.plotly_chart(style(fig, "Revenue"), use_container_width=True)

    # Each age group's revenue split across categories (rows add up to 100%)
    mix = filtered.groupby(["Age Group", "Product Category"], as_index=False)["Total Amount"].sum()
    mix["Share"] = mix["Total Amount"] / mix.groupby("Age Group")["Total Amount"].transform("sum") * 100
    fig = px.bar(mix, x="Age Group", y="Share", color="Product Category", barmode="group",
                 color_discrete_map=CATEGORY_COLORS,
                 category_orders={"Age Group": AGE_LABELS, "Product Category": list(CATEGORY_COLORS)})
    fig.update_traces(hovertemplate="Age %{x}<br>%{y:.1f}% of the group's revenue<extra></extra>")
    st.subheader("Category mix within each age group")
    st.plotly_chart(style(fig, "% of the age group's revenue"), use_container_width=True)

    st.info("Every customer in this dataset buys only once, and statistical tests found none of these "
            "age or gender differences to be significant (see customer_patterns.ipynb).")

# ---------- Tab 3: Data ----------
with data_tab:
    columns = ["Transaction ID", "Date", "Customer ID", "Gender", "Age", "Product Category",
               "Quantity", "Price per Unit", "Total Amount"]
    st.dataframe(filtered[columns], use_container_width=True, hide_index=True)
    st.download_button("Download filtered data (CSV)", filtered[columns].to_csv(index=False),
                       file_name="retail_sales_filtered.csv", mime="text/csv")
