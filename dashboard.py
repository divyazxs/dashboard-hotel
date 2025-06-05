# IMPORT LIBRARIES
import pandas as pd
import plotly.express as px
import streamlit as st

# Set the page configuration
custom_theme = {
    "primaryColor": "#EFF6E0",
    "backgroundColor": "#EFF6E0",
    "secondaryBackgroundColor": "#598392",
    "textColor": "#10175A",
    "font": "serif"
}
st.set_page_config(page_title="Hotel Booking Dashboard", layout="wide")
st.title("📊 Hotel Booking Analysis Dashboard")
st.markdown(
    """
    <style>
        .stApp {
            background-color: #f3d0a4;
        }
        .css-18e3th9 {
            background-color: #cfa093 !important;
        }
        .css-1d391kg {
            color: #660e60 !important;
        }
        .css-10trblm, .css-1v0mbdj {
            color: #660e60 !important;
        }
        .st-bb {
            color: #660e60 !important;
        }
        .st-bb:hover {
            color: #893f71 !important;
        }
        .st-cq {
            background-color: #ac6f82 !important;
        }
        .st-dx {
            background-color: #893f71 !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)   


# Load dataset
df = pd.read_csv(r"D:/SEMESTER 6/PPYTHON/DASHBOARD/hotel_booking.csv")

#Processing data
df['total_nights'] = df['stays_in_weekend_nights'] + df['stays_in_week_nights']
df['total_revenue'] = df['adr'] * df['total_nights']

# Sidebar filter
# 1. Filter tahun booking (rentang)
min_year = int(df['arrival_date_year'].min())
max_year = int(df['arrival_date_year'].max())
year_range = st.sidebar.slider(
    "Tahun Booking",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year),
    step=1
)

# 2. Filter hotel (multiple choose)
hotel_options = ['All'] + sorted(df['hotel'].unique())
selected_hotels = st.sidebar.selectbox(
    "Hotel",
    options=hotel_options,
    index=0
)

# 3. Filter customer segment (select one, ada opsi All)
segment_options = ['All'] + sorted(df['market_segment'].unique())
selected_segment = st.sidebar.selectbox(
    "Customer Segment",
    options=segment_options,
    index=0
)

# Terapkan filter ke dataframe
filtered_df = df[
    (df['arrival_date_year'] >= year_range[0]) &
    (df['arrival_date_year'] <= year_range[1])
]
if selected_hotels != 'All':
    filtered_df = filtered_df[filtered_df['hotel'] == selected_hotels]
if selected_segment != 'All':
    filtered_df = filtered_df[filtered_df['market_segment'] == selected_segment]

# Metrics
# Helper function to format revenue
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(
        label="Total Booking",
        value=f"{filtered_df.shape[0]:,}"
    )

with col2:
    total_revenue = filtered_df['total_revenue'].sum()
    if total_revenue >= 1_000_000_000:
        revenue_str = f"€ {total_revenue/1_000_000_000:.2f} B"
    elif total_revenue >= 1_000_000:
        revenue_str = f"€ {total_revenue/1_000_000:.2f} M"
    else:
        revenue_str = f"€ {total_revenue:,.2f}"
    st.metric(
        label="Total Pendapatan:",
        value=revenue_str
    )

with col3:
    avg_nights = filtered_df['total_nights'].mean()
    st.metric(
        label="Rata-rata Lama Menginap",
        value=f"{avg_nights:.0f} nights"
    )

# Pendapatan tiap bulan & status 
left_col, right_col = st.columns([2, 1])  # left column is twice as wide as right

with left_col:
    # Prepare monthly revenue data
    monthly_revenue = (
        filtered_df
        .groupby(['arrival_date_year', 'arrival_date_month'])
        .agg({'total_revenue': 'sum'})
        .reset_index()
    )
    # Convert month names to numbers for sorting
    monthly_revenue['month_num'] = monthly_revenue['arrival_date_month'].apply(lambda x: list(calendar.month_name).index(x))
    monthly_revenue = monthly_revenue.sort_values(['arrival_date_year', 'month_num'])
    # Create a label for x-axis
    monthly_revenue['year_month'] = monthly_revenue['arrival_date_year'].astype(str) + '-' + monthly_revenue['month_num'].astype(str).str.zfill(2)
    fig_line = px.line(
        monthly_revenue,
        x='year_month',
        y='total_revenue',
        markers=True,
        title="Pendapatan per Bulan",
        labels={'year_month': 'Tahun-Bulan', 'total_revenue': 'Pendapatan (€)'}
    )
    fig_line.update_traces(marker=dict(size=6, symbol='circle'))
    fig_line.update_layout(height=400)
    st.plotly_chart(fig_line, use_container_width=True)

with right_col:
    # Prepare booking status data
    status_counts = filtered_df['is_canceled'].value_counts().rename({0: 'Not Canceled', 1: 'Canceled'})
    fig_donut = px.pie(
        names=status_counts.index,
        values=status_counts.values,
        hole=0.5,
        title="Perbandingan Status Booking"
    )
    fig_donut.update_traces(textinfo='percent')
    fig_donut.update_layout(height=400, 
                            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),)
    st.plotly_chart(fig_donut, use_container_width=True)

# Dua chart:  (Bar) & Top 5 Negara (Bubble)
with st.container():
    col1, col2 = st.columns(2)

    with col1:
        # Ketidaksesuaian tipe kamar berdasarkan distribution chnannel
        # Hitung ketidaksesuaian tipe kamar (reserved != assigned) per distribution channel
        room_mismatch = filtered_df[filtered_df['reserved_room_type'] != filtered_df['assigned_room_type']]
        mismatch_counts = room_mismatch['distribution_channel'].value_counts().reset_index()
        mismatch_counts.columns = ['distribution_channel', 'count']

        fig_bar = px.bar(
            mismatch_counts,
            x='distribution_channel',
            y='count',
            title="Jumlah Ketidaksesuaian Tipe Kamar per Distribution Channel",
            labels={'distribution_channel': 'Distribution Channel', 'count': 'Jumlah Ketidaksesuaian'},
            color='distribution_channel',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_bar.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        # Top 5 Countries by Booking Count
        top_countries = filtered_df['country'].value_counts().head(5)
        fig_bubble = px.scatter(
            top_countries,
            x=top_countries.index,
            y=top_countries.values,
            size=top_countries.values,
            title="Top 5 Negara Berdasarkan Jumlah Booking",
            labels={'x': 'Negara', 'y': 'Jumlah Booking'},
            color_discrete_sequence=['#4682B4']
        )
        fig_bubble.update_layout(height=400)
        st.plotly_chart(fig_bubble, use_container_width=True)
