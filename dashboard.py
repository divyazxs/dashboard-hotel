# IMPORT LIBRARIES
import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
import calendar

# Set the page configuration
st.set_page_config(page_title="Hotel Booking Dashboard", layout="wide")
st.title("🏨 Hotel Booking Analysis Dashboard")
# Custom CSS for background and sidebar
st.markdown(
    '''
    <style>
        .main {
            background-color: #e6d7ca;
        }
        [data-testid="stSidebar"] {
            background-color: #e6d7ca;
        }
    </style>
    ''',
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

# 2. Filter metric
metric = st.sidebar.radio("Metric:", ["Revenue", "Booking"])
# Metric-based aggregation
if metric == "Revenue":
    value_col = "total_revenue"
    agg_func = "sum"
else:
    value_col = "hotel"  # proxy for booking count (will be counted per row)
    agg_func = "count"

# Terapkan filter ke dataframe
filtered_df = df[
    (df['arrival_date_year'] >= year_range[0]) &
    (df['arrival_date_year'] <= year_range[1])
]
filtered_df = filtered_df[filtered_df['reservation_status'] != 'Canceled']

# KPI
# Helper function to format revenue
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(
        label="Total Bookings",
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
        label="Total Revenue:",
        value=revenue_str
    )

with col3:
    avg_nights = filtered_df['total_nights'].mean()
    st.metric(
        label="Average Nights Stayed:",
        value=f"{avg_nights:.0f} nights"
    )

# Plot bagian atas: Line Chart (Pendapatan/Booking per Bulan) & Donut Chart (Hotel Type)
left_col, right_col = st.columns([2, 1])

with left_col:
    # Prepare monthly revenue data
    monthly_revenue = (
        filtered_df
        .groupby(['arrival_date_year', 'arrival_date_month'])
        .agg({value_col: agg_func})
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
        y= value_col,
        markers=True,
        title='Revenue per Month' if metric == "Revenue" else 'Booking per Month',
        template="plotly_white",
        labels={
            'year_month': 'Period',
            value_col: 'Revenue (€)' if metric == "Revenue" else 'Total Booking', 
        }, 
        color_discrete_sequence=['#8c6d5c', '#c9a66b']
    )
    fig_line.update_traces(marker=dict(size=6, symbol='circle'))
    if metric == "Revenue":
        fig_line.update_traces(
        hovertemplate='Periode=%{x}<br>Pendapatan (€) = %{y:.2s}<extra></extra>'
        )
    else:  # Total Booking
        fig_line.update_traces(
        hovertemplate='Periode=%{x}<br>Total Booking = %{y:,.0f}<extra></extra>'
        )
    fig_line.update_layout(yaxis_tickformat=",")  # format angka biasa dengan ribuan
    fig_line.update_layout(paper_bgcolor='#fff7e6')
    fig_line.update_layout(height=400)
    st.plotly_chart(fig_line, use_container_width=True)

with right_col:
    # Prepare hotel type data
    hotel_type = filtered_df.groupby('hotel').agg({value_col: agg_func})
    fig_donut = px.pie(
    names=hotel_type.index,
    values=hotel_type[value_col],
    hole=0.5,
    title=f"Hotel Type by {metric}",
    template="plotly_white", 
    labels={
        'hotel': 'Type Hotel',
        value_col: 'Revenue (€)' if metric == "Revenue" else 'Total Booking'
        }, 
    color_discrete_sequence=["#d9a066", "#a1c181"]
    )
    fig_donut.update_traces(textinfo='percent')
    if metric == "Revenue":
        fig_donut.update_traces(
        hovertemplate='Type Hotel = %{label}<br>Revenue (€) = %{value:.2s}<extra></extra>'
        )
    else:  # Total Booking
        fig_donut.update_traces(
        hovertemplate='Type Hotel = %{label}<br>Total Booking = %{value:,.0f}<extra></extra>'
        )    
    fig_donut.update_layout(height=400, 
                            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),)
    fig_donut.update_layout(paper_bgcolor='#fff7e6')
    st.plotly_chart(fig_donut, use_container_width=True)

# Plot bagian bawah: Bubble Chart (Top 5 Countries) & Bar Chart (Distribution Channel)
with st.container():
    col1, col2 = st.columns(2)

    with col1: 
        # Top 5 Countries by Booking Count
        country_data = filtered_df.groupby('country').agg({value_col: agg_func}).reset_index()
        top_country = country_data.sort_values(by=value_col, ascending=False).head(5)

        np.random.seed(42)  # untuk hasil reproducible
        top_country['x'] = np.random.uniform(0, 10, size=len(top_country))
        top_country['y'] = np.random.uniform(0, 10, size=len(top_country))
        
        # Bubble Chart
        fig_bubble = px.scatter(
        top_country,
        x='x', 
        y='y',  
        size=value_col,
        text = 'country',
        color='country',
        hover_name='country',
        size_max=70,
        title=f"Top 5 Countries by {metric}",
        template='plotly_white',
        labels={
            'country': 'Country',
            value_col: 'Revenue (€)' if metric == "Revenue" else 'Total Booking'
            }, 
        color_discrete_sequence=["#80ced6", "#ffb3ab", "#f3d250", "#c9cba3", "#e0bbe4"]
        )

        fig_bubble.update_traces(marker=dict(opacity=0.9, line=dict(width=2, color='white')))
        if metric == "Revenue":
            fig_bubble.update_traces(
            hovertemplate='Country = %{hovertext}<br>Revenue (€) = %{marker.size:.2s}<extra></extra>'
            )
        else:  # Total Booking
            fig_bubble.update_traces(
            hovertemplate='Country = %{hovertext}<br>Total Booking = %{marker.size:,.0f}<extra></extra>'
            )
        fig_bubble.update_layout(
        showlegend=True,
        height=400,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        paper_bgcolor='#fff7e6', 
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_bubble, use_container_width=True)

    with col2:
        filtered_df2 = filtered_df.copy()
        filtered_df2['hotel2'] = filtered_df2['hotel']

        if 'hotel2' in filtered_df2.index.names:
            filtered_df2.reset_index(inplace=True)

        segment_hotel_data = (
            filtered_df2.groupby(['market_segment', 'hotel2'])[value_col]
            .agg(agg_func)
            .reset_index()
            )
        
        segment_hotel_data.rename(columns={value_col: 'value'}, inplace=True)

        segment_order = (
            segment_hotel_data.groupby('market_segment')['value']
            .sum()
            .sort_values(ascending=False)
            .index.tolist()
            )
        
        bar_fig = px.bar(
            segment_hotel_data,
            x='market_segment',
            y='value',
            color='hotel2',
            hover_data=['hotel2'],
            barmode='stack',
            title=f'Market Segment by Hotel Type and {metric}',
            template="plotly_white",
            labels={
                'market_segment': 'Market Segment',
                'value': 'Revenue (€)' if metric == "Revenue" else 'Total Booking'
            },
            category_orders={'market_segment': segment_order},
            color_discrete_sequence=["#d9a066", "#a1c181"]
            )
        bar_fig.update_layout(paper_bgcolor='#fff7e6')
        if metric == "Revenue":
            bar_fig.update_traces(
                hovertemplate='Market Segment = %{x}<br>Hotel Type = %{customdata[0]}<br>Revenue (€) = %{y:.2s}<extra></extra>'
            )
        else:  # Total Booking
            bar_fig.update_traces(
                hovertemplate='Market Segment = %{x}<br>Hotel Type = %{customdata[0]}<br>Total Booking = %{y:,.0f}<extra></extra>'
            )
        bar_fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(bar_fig, use_container_width=True)

       
        
