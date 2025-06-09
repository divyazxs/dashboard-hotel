# === IMPORT LIBRARY ===
import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
import calendar

# === PAGE CONFIGURATION ===
st.set_page_config(
    page_title="Hotel Booking Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🏨"
)

# === CUSTOM CSS ===
st.markdown(
    '''
    <style>
        /* Main background and font settings */
        .main {
            background: linear-gradient(135deg, #0f1116 0%, #1c2526 100%);
            color: #FFFFFF;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1c2526 0%, #0f1116 100%);
            box-shadow: 2px 0 10px rgba(0, 0, 0, 0.5);
            padding: 20px;
        }
        [data-testid="stSidebar"] .stRadio > div {
            background-color: #2a2f3a;
            border-radius: 8px;
            padding: 10px;
        }
        [data-testid="stSidebar"] .stSlider > div {
            background-color: #2a2f3a;
            border-radius: 8px;
            padding: 10px;
        }

        /* Header styling */
        h1 {
            color: #FFD700;
            font-size: 2.5em;
            text-align: center;
            text-shadow: 0 0 10px rgba(255, 215, 0, 0.5);
            animation: fadeIn 1.5s ease-in-out;
        }
        h2, h3 {
            color: #FFD700;
            font-weight: 500;
        }

        /* Metric cards */
        .stMetric {
            background: linear-gradient(45deg, #1c2526, #2a2f3a);
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
            transition: transform 0.3s ease;
        }
        .stMetric:hover {
            transform: translateY(-5px);
        }

        /* Chart containers */
        .plotly-chart {
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
        }

        /* Buttons and inputs */
        .stButton > button {
            background-color: #FFD700;
            color: #0f1116;
            border-radius: 8px;
            font-weight: bold;
            transition: background-color 0.3s ease;
        }
        .stButton > button:hover {
            background-color: #FFC107;
        }

        /* Animation keyframes */
        @keyframes fadeIn {
            0% { opacity: 0; }
            100% { opacity: 1; }
        }

        /* General layout */
        .block-container {
            padding: 2rem;
            max-width: 1400px;
            margin: auto;
        }

        /* Footer */
        .footer {
            text-align: center;
            color: #AAAAAA;
            font-size: 0.9em;
            margin-top: 2rem;
            padding: 1rem;
            border-top: 1px solid #2a2f3a;
        }
    </style>
    ''',
    unsafe_allow_html=True
)

# === HEADER ===
st.markdown(
    """
    <div style='text-align: center; margin-bottom: 2rem;'>
        <h1> Hotel Analysis Dashboard </h1>
        <p style='color: #AAAAAA; font-size: 1.1em;'> by Achmad Rivqi, Divya Zahranika, and Syafira Nauroh Hamidah</p>
    </div>
    """,
    unsafe_allow_html=True
)

# === LOAD DATA ===
@st.cache_data
def load_data():
    df = pd.read_csv('hotel_booking.csv')
    df['total_nights'] = df['stays_in_weekend_nights'] + df['stays_in_week_nights']
    df['total_revenue'] = df['adr'] * df['total_nights']
    return df

df = load_data()

# === SIDEBAR FILTER ===
with st.sidebar:
    st.markdown(
        """
        <div style='text-align: center; margin-bottom: 1rem;'>
            <h2>🎛 Control Panel</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

    min_year = int(df['arrival_date_year'].min())
    max_year = int(df['arrival_date_year'].max())
    year_range = st.slider(
        "📅 Booking Year Range",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year),
        step=1,
        help="Select the range of years to analyze"
    )

    metric = st.radio(
        "📊 Select Metric",
        ["Revenue", "Booking"],
        help="Choose between revenue or booking count"
    )
    value_col = "total_revenue" if metric == "Revenue" else "total_nights"  # Changed to total_nights for Booking
    agg_func = "sum" if metric == "Revenue" else "count"

    st.markdown("---")
    st.markdown(
        "<p style='text-align: center; color: #AAAAAA;'>Hotel Analytics</p>",
        unsafe_allow_html=True
    )

# === DATA FILTERING ===
filtered_df = df[
    (df['arrival_date_year'] >= year_range[0]) &
    (df['arrival_date_year'] <= year_range[1])
]
filtered_df = filtered_df[filtered_df['reservation_status'] != 'Canceled']

# === METRICS DISPLAY ===
st.markdown("### Key Performance Indicators")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(
        label="🏨 Total Bookings",
        value=f"{filtered_df.shape[0]:,}",
        delta=None,
        help="Total number of bookings"
    )

with col2:
    total_revenue = filtered_df['total_revenue'].sum()
    revenue_str = f"€ {total_revenue/1_000_000:.2f}M" if total_revenue >= 1_000_000 else f"€ {total_revenue:,.2f}"
    st.metric(
        label="💰 Total Revenue",
        value=revenue_str,
        delta=None,
        help="Total revenue generated"
    )

with col3:
    avg_nights = filtered_df['total_nights'].mean()
    st.metric(
        label="🌙 Avg. Nights Stayed",
        value=f"{int(avg_nights)} nights",
        delta=None,
        help="Average length of stay"
    )

# === CHART 1: LINE (REVENUE / BOOKING PER BULAN) ===
st.markdown("### Monthly Performance Trend")
monthly = (
    filtered_df.groupby(['arrival_date_year', 'arrival_date_month'])
    .agg({value_col: agg_func})
    .reset_index()
)
monthly['month_num'] = monthly['arrival_date_month'].apply(lambda x: list(calendar.month_name).index(x))
monthly['year_month'] = (
    monthly['arrival_date_year'].astype(str) + '-' +
    monthly['month_num'].astype(str).str.zfill(2)
)
monthly = monthly.sort_values(['arrival_date_year', 'month_num'])

fig_line = px.line(
    monthly,
    x='year_month',
    y=value_col,
    markers=True,
    title=f"📈 {'Revenue' if metric == 'Revenue' else 'Booking'} Over Time",
    template='plotly_dark',
    labels={'year_month': 'Month', value_col: '€ Revenue' if metric == "Revenue" else 'Total Booking'},
    color_discrete_sequence=['#FFD700']
)
fig_line.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    height=500,
    font=dict(color='#FFFFFF'),
    xaxis_tickangle=45,
    showlegend=False
)
fig_line.update_traces(
    line=dict(width=3),
    marker=dict(size=10, symbol='circle', line=dict(width=2, color='#0f1116'))
)

# === CHART 2: DONUT ===
hotel_type = filtered_df.groupby('hotel').agg({value_col: agg_func}).reset_index()
# Rename the aggregated column to avoid conflict with 'hotel'
hotel_type = hotel_type.rename(columns={value_col: f"{metric.lower()}_total"})
fig_donut = px.pie(
    hotel_type,
    names='hotel',
    values=f"{metric.lower()}_total",
    hole=0.5,
    title=f"🏨 Hotel Distribution by {metric}",
    template="plotly_dark",
    color_discrete_sequence=["#FFD700", "#4682B4"]
)
fig_donut.update_traces(
    textinfo='percent+label',
    textfont_size=18,  # Increased from 14 to 18 for better readability
    marker=dict(line=dict(color='#0f1116', width=2))
)
fig_donut.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',
    height=600,  # Increased from 500 to 600 for larger size
    font=dict(color='#FFFFFF')
)

# === DISPLAY TOP CHARTS ===
col1, col2 = st.columns([1.5, 1.5])  # Changed from [2, 1] to [1.5, 1.5] for balanced enlargement
with col1:
    st.plotly_chart(fig_line, use_container_width=True, theme=None)
with col2:
    st.plotly_chart(fig_donut, use_container_width=True, theme=None)

# === CHART 3: BUBBLE COUNTRY ===
st.markdown("### Global Insights")
top_country = (
    filtered_df.groupby('country')
    .agg({value_col: agg_func})
    .sort_values(by=value_col, ascending=False)
    .reset_index()
    .head(5)
)
np.random.seed(42)
top_country['x'] = np.random.uniform(0, 10, size=5)
top_country['y'] = np.random.uniform(0, 10, size=5)
fig_bubble = px.scatter(
    top_country,
    x='x', y='y',
    size=value_col,
    color='country',
    text='country',
    title=f"🌍 Top 5 Countries by {metric}",
    template="plotly_dark",
    size_max=100,
    color_discrete_sequence=px.colors.qualitative.Bold
)
fig_bubble.update_layout(
    height=500,
    paper_bgcolor='rgba(0,0,0,0)',
    xaxis=dict(visible=False),
    yaxis=dict(visible=False),
    font=dict(color='#FFFFFF')
)
fig_bubble.update_traces(
    textposition='middle center',
    textfont=dict(size=14, color='#FFFFFF')
)

# === CHART 4: MARKET SEGMENT BAR ===
segment_data = (
    filtered_df.groupby(['market_segment', 'hotel'])[value_col]
    .agg(agg_func)
    .reset_index()
)
segment_data.rename(columns={value_col: f"{metric.lower()}_total"}, inplace=True)

fig_bar = px.bar(
    segment_data,
    x='market_segment',
    y=f"{metric.lower()}_total",
    color='hotel',
    barmode='stack',
    title=f"📊 Market Segments by Hotel and {metric}",
    template='plotly_dark',
    color_discrete_sequence=['#FFD700', '#4682B4']
)
fig_bar.update_layout(
    height=500,
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#FFFFFF'),
    xaxis_tickangle=45
)
fig_bar.update_traces(
    marker=dict(line=dict(color='#0f1116', width=1))
)

# === DISPLAY BOTTOM CHARTS ===
col3, col4 = st.columns(2)
with col3:
    st.plotly_chart(fig_bubble, use_container_width=True, theme=None)
with col4:
    st.plotly_chart(fig_bar, use_container_width=True, theme=None)

# === FOOTER ===
st.markdown(
    """
    <div class='footer'>
        <p>© Project Python 2025 | Designed by Group 8</p>
    </div>
    """,
    unsafe_allow_html=True
)
