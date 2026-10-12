import os
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
from urllib.parse import quote_plus


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Hotel Booking Analysis",
    page_icon="🏨",
    layout="wide"
)


# ============================================================
# MYSQL CONFIGURATION
# Use the same credentials as create_database.sql
# ============================================================

DB_HOST = "localhost"
DB_PORT = 3306
DB_USER = "hotel_user"
DB_PASSWORD = os.environ["HOTEL_DB_PASSWORD"]
DB_NAME = "hotel_booking_analysis"
TABLE_NAME = "hotel_bookings"


# ============================================================
# DATABASE CONNECTION
# ============================================================

@st.cache_resource
def get_engine():
    password = quote_plus(DB_PASSWORD)

    return create_engine(
        f"mysql+pymysql://{DB_USER}:{password}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
        pool_pre_ping=True
    )


@st.cache_data(ttl=600)
def load_data():
    engine = get_engine()
    query = f"SELECT * FROM {TABLE_NAME}"
    return pd.read_sql(query, engine)


# ============================================================
# DATA PREPARATION
# ============================================================

def prepare_data(data):
    df = data.copy()

    # Remove duplicate records
    df = df.drop_duplicates().copy()

    numeric_columns = [
        "is_canceled",
        "lead_time",
        "arrival_date_year",
        "arrival_date_day_of_month",
        "stays_in_weekend_nights",
        "stays_in_week_nights",
        "adults",
        "children",
        "babies",
        "is_repeated_guest",
        "previous_cancellations",
        "previous_bookings_not_canceled",
        "booking_changes",
        "days_in_waiting_list",
        "adr",
        "required_car_parking_spaces",
        "total_of_special_requests"
    ]

    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    # Missing values
    df["children"] = df["children"].fillna(0)
    df["country"] = df["country"].fillna("Unknown")

    # Arrival date
    df["arrival_date"] = pd.to_datetime(
        df["arrival_date_year"].astype("Int64").astype(str)
        + "-"
        + df["arrival_date_month"].astype(str)
        + "-"
        + df["arrival_date_day_of_month"].astype("Int64").astype(str),
        errors="coerce"
    )

    # Remove bookings with no guests
    df = df[
        (
            df["adults"].fillna(0)
            + df["children"].fillna(0)
            + df["babies"].fillna(0)
        ) > 0
    ].copy()

    # Handle invalid ADR
    df.loc[df["adr"] < 0, "adr"] = np.nan
    df["adr"] = df["adr"].fillna(df["adr"].median())

    # Total stay
    df["total_stay"] = (
        df["stays_in_weekend_nights"].fillna(0)
        + df["stays_in_week_nights"].fillna(0)
    )

    # Cancellation label
    df["cancellation_status"] = np.where(
        df["is_canceled"] == 1,
        "Cancelled",
        "Not Cancelled"
    )

    # Outlier handling
    for column in ["lead_time", "adr", "total_stay"]:
        q1 = df[column].quantile(0.25)
        q3 = df[column].quantile(0.75)
        iqr = q3 - q1

        lower = max(0, q1 - 1.5 * iqr)
        upper = q3 + 1.5 * iqr

        df[f"{column}_clean"] = df[column].clip(
            lower=lower,
            upper=upper
        )

    return df


# ============================================================
# LOAD DATA
# ============================================================

st.title("🏨 Hotel Booking Analysis")
st.caption("Understanding Customer Behavior and Cancellation Trends")

try:
    df = prepare_data(load_data())
except Exception as error:
    st.error("Unable to connect to MySQL or load the hotel_bookings table.")
    st.code(str(error))
    st.stop()


# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.header("🔎 Dashboard Filters")

hotel_options = sorted(df["hotel"].dropna().unique().tolist())
selected_hotels = st.sidebar.multiselect(
    "Hotel Type",
    hotel_options,
    default=hotel_options
)

year_options = sorted(
    df["arrival_date_year"].dropna().astype(int).unique().tolist()
)
selected_years = st.sidebar.multiselect(
    "Arrival Year",
    year_options,
    default=year_options
)

month_order = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

available_months = [
    month for month in month_order
    if month in df["arrival_date_month"].dropna().unique()
]

selected_months = st.sidebar.multiselect(
    "Arrival Month",
    available_months,
    default=available_months
)

market_options = sorted(
    df["market_segment"].dropna().unique().tolist()
)
selected_markets = st.sidebar.multiselect(
    "Market Segment",
    market_options,
    default=market_options
)

customer_options = sorted(
    df["customer_type"].dropna().unique().tolist()
)
selected_customers = st.sidebar.multiselect(
    "Customer Type",
    customer_options,
    default=customer_options
)

selected_status = st.sidebar.selectbox(
    "Booking Status",
    ["All", "Cancelled", "Not Cancelled"]
)

lead_min = int(df["lead_time"].min())
lead_max = int(df["lead_time"].max())

selected_lead_time = st.sidebar.slider(
    "Lead Time (Days)",
    min_value=lead_min,
    max_value=lead_max,
    value=(lead_min, lead_max)
)


# ============================================================
# APPLY FILTERS
# ============================================================

filtered_df = df[
    df["hotel"].isin(selected_hotels)
    & df["arrival_date_year"].isin(selected_years)
    & df["arrival_date_month"].isin(selected_months)
    & df["market_segment"].isin(selected_markets)
    & df["customer_type"].isin(selected_customers)
    & df["lead_time"].between(
        selected_lead_time[0],
        selected_lead_time[1]
    )
].copy()

if selected_status != "All":
    filtered_df = filtered_df[
        filtered_df["cancellation_status"] == selected_status
    ]

if filtered_df.empty:
    st.warning("No bookings match the selected filters.")
    st.stop()


# ============================================================
# KPI METRICS
# ============================================================

total_bookings = len(filtered_df)
cancelled_bookings = int(filtered_df["is_canceled"].sum())
cancellation_rate = (
    cancelled_bookings / total_bookings * 100
    if total_bookings > 0
    else 0
)
average_adr = filtered_df["adr"].mean()
average_lead_time = filtered_df["lead_time"].mean()

st.subheader("📌 Key Performance Indicators")

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

kpi1.metric(
    "Total Bookings",
    f"{total_bookings:,}"
)

kpi2.metric(
    "Cancelled Bookings",
    f"{cancelled_bookings:,}"
)

kpi3.metric(
    "Cancellation Rate",
    f"{cancellation_rate:.1f}%"
)

kpi4.metric(
    "Average ADR",
    f"{average_adr:.2f}"
)

kpi5.metric(
    "Average Lead Time",
    f"{average_lead_time:.1f} days"
)


# ============================================================
# DASHBOARD TABS
# ============================================================

overview_tab, trends_tab, behavior_tab, insights_tab = st.tabs(
    [
        "📊 Overview",
        "📈 Booking Trends",
        "👥 Customer Behavior",
        "💡 Insights"
    ]
)


# ============================================================
# TAB 1 - OVERVIEW
# ============================================================

with overview_tab:

    col1, col2 = st.columns(2)

    with col1:
        status_counts = (
            filtered_df["cancellation_status"]
            .value_counts()
            .rename_axis("Booking Status")
            .reset_index(name="Bookings")
        )

        fig_status = px.pie(
            status_counts,
            names="Booking Status",
            values="Bookings",
            hole=0.42,
            title="Cancellation Status"
        )

        fig_status.update_layout(
            legend_title_text="Booking Status"
        )

        st.plotly_chart(
            fig_status,
            use_container_width=True
        )

    with col2:
        hotel_summary = (
            filtered_df.groupby("hotel", observed=False)
            .agg(
                total_bookings=("is_canceled", "size"),
                cancellations=("is_canceled", "sum")
            )
            .reset_index()
        )

        hotel_summary["cancellation_rate"] = (
            hotel_summary["cancellations"]
            / hotel_summary["total_bookings"]
            * 100
        )

        fig_hotel = px.bar(
            hotel_summary,
            x="hotel",
            y="cancellation_rate",
            text_auto=".1f",
            title="Cancellation Rate by Hotel Type",
            labels={
                "hotel": "Hotel Type",
                "cancellation_rate": "Cancellation Rate (%)"
            }
        )

        fig_hotel.update_layout(
            yaxis_title="Cancellation Rate (%)"
        )

        st.plotly_chart(
            fig_hotel,
            use_container_width=True
        )

    segment_summary = (
        filtered_df.groupby("market_segment", observed=False)
        .agg(
            total_bookings=("is_canceled", "size"),
            cancellations=("is_canceled", "sum")
        )
        .reset_index()
    )

    segment_summary["cancellation_rate"] = (
        segment_summary["cancellations"]
        / segment_summary["total_bookings"]
        * 100
    )

    segment_summary = segment_summary.sort_values(
        "cancellation_rate",
        ascending=False
    )

    fig_segment = px.bar(
        segment_summary,
        x="market_segment",
        y="cancellation_rate",
        color="total_bookings",
        text_auto=".1f",
        title="Cancellation Rate by Market Segment",
        labels={
            "market_segment": "Market Segment",
            "cancellation_rate": "Cancellation Rate (%)",
            "total_bookings": "Bookings"
        }
    )

    st.plotly_chart(
        fig_segment,
        use_container_width=True
    )


# ============================================================
# TAB 2 - BOOKING TRENDS
# ============================================================

with trends_tab:

    trend_df = (
        filtered_df.dropna(subset=["arrival_date"])
        .assign(
            arrival_month=lambda x:
            x["arrival_date"].dt.to_period("M").astype(str)
        )
        .groupby("arrival_month", observed=False)
        .agg(
            total_bookings=("is_canceled", "size"),
            cancellations=("is_canceled", "sum")
        )
        .reset_index()
    )

    fig_trend = go.Figure()

    fig_trend.add_trace(
        go.Scatter(
            x=trend_df["arrival_month"],
            y=trend_df["total_bookings"],
            mode="lines+markers",
            name="Total Bookings"
        )
    )

    fig_trend.add_trace(
        go.Scatter(
            x=trend_df["arrival_month"],
            y=trend_df["cancellations"],
            mode="lines+markers",
            name="Cancellations"
        )
    )

    fig_trend.update_layout(
        title="Monthly Booking and Cancellation Trend",
        xaxis_title="Arrival Month",
        yaxis_title="Number of Bookings",
        hovermode="x unified"
    )

    st.plotly_chart(
        fig_trend,
        use_container_width=True
    )

    monthly_summary = (
        filtered_df.groupby(
            "arrival_date_month",
            observed=False
        )
        .size()
        .reindex(available_months)
        .dropna()
        .reset_index(name="bookings")
    )

    fig_month = px.bar(
        monthly_summary,
        x="arrival_date_month",
        y="bookings",
        text_auto=True,
        title="Bookings by Arrival Month",
        labels={
            "arrival_date_month": "Month",
            "bookings": "Bookings"
        }
    )

    st.plotly_chart(
        fig_month,
        use_container_width=True
    )


# ============================================================
# TAB 3 - CUSTOMER BEHAVIOR
# ============================================================

with behavior_tab:

    col1, col2 = st.columns(2)

    with col1:
        fig_lead = px.histogram(
            filtered_df,
            x="lead_time_clean",
            color="cancellation_status",
            nbins=40,
            barmode="overlay",
            title="Lead Time Distribution by Booking Status",
            labels={
                "lead_time_clean": "Lead Time (Days)",
                "cancellation_status": "Booking Status"
            }
        )

        st.plotly_chart(
            fig_lead,
            use_container_width=True
        )

    with col2:
        fig_adr = px.box(
            filtered_df,
            x="hotel",
            y="adr_clean",
            color="cancellation_status",
            points=False,
            title="ADR by Hotel and Booking Status",
            labels={
                "hotel": "Hotel Type",
                "adr_clean": "ADR",
                "cancellation_status": "Booking Status"
            }
        )

        st.plotly_chart(
            fig_adr,
            use_container_width=True
        )

    customer_summary = (
        filtered_df.groupby("customer_type", observed=False)
        .agg(
            total_bookings=("is_canceled", "size"),
            cancellations=("is_canceled", "sum"),
            average_adr=("adr", "mean"),
            average_special_requests=(
                "total_of_special_requests",
                "mean"
            )
        )
        .reset_index()
    )

    customer_summary["cancellation_rate"] = (
        customer_summary["cancellations"]
        / customer_summary["total_bookings"]
        * 100
    )

    fig_customer = px.bar(
        customer_summary.sort_values(
            "cancellation_rate",
            ascending=False
        ),
        x="customer_type",
        y="cancellation_rate",
        color="average_adr",
        text_auto=".1f",
        title="Cancellation Rate by Customer Type",
        labels={
            "customer_type": "Customer Type",
            "cancellation_rate": "Cancellation Rate (%)",
            "average_adr": "Average ADR"
        }
    )

    st.plotly_chart(
        fig_customer,
        use_container_width=True
    )

    repeated_summary = (
        filtered_df.groupby(
            "is_repeated_guest",
            observed=False
        )["is_canceled"]
        .agg(["count", "mean"])
        .reset_index()
        .rename(
            columns={
                "count": "total_bookings",
                "mean": "cancellation_rate"
            }
        )
    )

    repeated_summary["Guest Type"] = repeated_summary[
        "is_repeated_guest"
    ].map({
        0: "New Guest",
        1: "Repeated Guest"
    })

    repeated_summary["cancellation_rate"] *= 100

    fig_repeat = px.bar(
        repeated_summary,
        x="Guest Type",
        y="cancellation_rate",
        text_auto=".1f",
        title="Cancellation Rate: New vs Repeated Guests",
        labels={
            "cancellation_rate": "Cancellation Rate (%)"
        }
    )

    st.plotly_chart(
        fig_repeat,
        use_container_width=True
    )


# ============================================================
# TAB 4 - DYNAMIC INSIGHTS AND RECOMMENDATIONS
# ============================================================

with insights_tab:

    st.subheader("Key Observations")

    hotel_rates = (
        filtered_df.groupby("hotel", observed=False)["is_canceled"]
        .mean()
        .mul(100)
        .sort_values(ascending=False)
    )

    highest_hotel = hotel_rates.index[0]
    highest_hotel_rate = hotel_rates.iloc[0]

    market_rates = (
        filtered_df.groupby(
            "market_segment",
            observed=False
        )["is_canceled"]
        .agg(["count", "mean"])
    )

    eligible_market_rates = market_rates[
        market_rates["count"] >= 100
    ].copy()

    if eligible_market_rates.empty:
        eligible_market_rates = market_rates[
            market_rates["count"] > 0
        ].copy()

    eligible_market_rates["mean"] *= 100

    highest_market = eligible_market_rates["mean"].idxmax()

    highest_market_rate = eligible_market_rates.loc[
        highest_market,
        "mean"
    ]

    cancelled_data = filtered_df[
        filtered_df["is_canceled"] == 1
    ]

    not_cancelled_data = filtered_df[
        filtered_df["is_canceled"] == 0
    ]

    cancelled_lead = cancelled_data["lead_time"].mean()
    confirmed_lead = not_cancelled_data["lead_time"].mean()

    cancelled_requests = cancelled_data[
        "total_of_special_requests"
    ].mean()

    confirmed_requests = not_cancelled_data[
        "total_of_special_requests"
    ].mean()

    monthly_counts = (
        filtered_df.groupby(
            "arrival_date_month",
            observed=False
        )
        .size()
        .reindex(month_order)
        .dropna()
    )

    peak_month = monthly_counts.idxmax()
    peak_bookings = int(monthly_counts.max())

    st.markdown(
        f"""
1. **Overall cancellation rate:** {cancellation_rate:.2f}% of the currently filtered bookings were cancelled.
2. **Hotel comparison:** {highest_hotel} has the highest cancellation rate at {highest_hotel_rate:.2f}%.
3. **Market segment:** {highest_market} has the highest cancellation rate at {highest_market_rate:.2f}% within the selected data.
4. **Lead time:** Cancelled bookings have an average lead time of {cancelled_lead:.2f} days, compared with {confirmed_lead:.2f} days for non-cancelled bookings.
5. **Peak demand:** {peak_month} has the highest booking volume with {peak_bookings:,} bookings.
6. **Special requests:** Cancelled bookings average {cancelled_requests:.2f} special requests, compared with {confirmed_requests:.2f} for non-cancelled bookings.
"""
    )

    st.subheader("Recommendations")

    st.markdown(
        f"""
- Focus cancellation-reduction actions on **{highest_hotel}** and the **{highest_market}** market segment.
- Use booking reminders and reconfirmation for customers with longer lead times.
- Align staffing and operational capacity with high-demand periods such as **{peak_month}**.
- Monitor ADR, customer type, repeated-guest status and special-request patterns together with cancellation rates when reviewing booking strategy.
"""
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()
st.caption(
    "Hotel Booking Analysis Dashboard | Data source: MySQL hotel_bookings table"
)
