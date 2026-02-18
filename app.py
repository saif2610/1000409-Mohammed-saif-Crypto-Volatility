import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

# --- Configuration ---
st.set_page_config(
    page_title="Crypto Volatility Visualizer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Styling ---
st.title("📈 Crypto Volatility Visualizer")
st.markdown("""
Simulating Market Swings with Mathematics for AI and Python  
Analyze cryptocurrency volatility using real market data and mathematical models.
""")

# --- Sidebar: Controls ---
st.sidebar.header("🎛️ Dashboard Controls")

# Pattern Selection
st.sidebar.subheader("Analysis Mode")
mode = st.sidebar.radio(
    "Choose Analysis Mode:",
    ("Real Data Analysis", "Mathematical Simulation")
)

# Mathematical Simulation Controls
st.sidebar.subheader("Simulation Parameters")
amplitude = st.sidebar.slider("Amplitude (Swing Size)", 10, 500, 100, 
                             help="Controls the magnitude of price swings")
frequency = st.sidebar.slider("Frequency (Swing Speed)", 0.1, 5.0, 1.0, 
                              help="Controls how often price swings occur")
drift = st.sidebar.slider("Drift (Long-term Trend)", -2.0, 2.0, 0.1, 
                         help="Controls the overall upward or downward slope")

st.sidebar.divider()

# Data Subset Selection
st.sidebar.subheader("Data Range")
time_range = st.sidebar.selectbox(
    "Time Period:",
    ("Last 1000 records", "Last 500 records", "Last 200 records", "All data"),
    index=0
)

# --- Stage 4: Data Preparation & Exploration ---
@st.cache_data
def load_and_prepare_data():
    """Load and clean cryptocurrency data."""
    try:
        # Load dataset
        df = pd.read_csv("crypto_Currency_data.csv")
        
        # Check columns
        st.subheader("📊 Dataset Information")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Rows", f"{df.shape[0]:,}")
        col2.metric("Total Columns", df.shape[1])
        col3.metric("Columns", ", ".join(df.columns.tolist()))
        
        # Display first few rows
        with st.expander("🔍 Preview Raw Data"):
            st.dataframe(df.head(), use_container_width=True)
        
        # Convert Timestamp from Unix to datetime
        if 'Timestamp' in df.columns:
            df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='s')
        
        # Rename columns for clarity
        rename_dict = {
            'Close': 'Close Price',
            'Open': 'Open Price',
            'High': 'High Price',
            'Low': 'Low Price',
            'Volume_(BTC)': 'Volume BTC',
            'Volume_BTC': 'Volume BTC',
            'Volume': 'Volume BTC',
            'Volume_(Currency)': 'Volume Currency',
            'Volume_Currency': 'Volume Currency'
        }
        
        # Apply renaming only for columns that exist
        existing_rename = {k: v for k, v in rename_dict.items() if k in df.columns}
        df = df.rename(columns=existing_rename)
        
        # Handle missing data
        missing_values = df.isnull().sum()
        if missing_values.sum() > 0:
            st.warning(f"Found {missing_values.sum()} missing values. Dropping them...")
            df = df.dropna()
        
        # Sort by timestamp
        if 'Timestamp' in df.columns:
            df = df.sort_values('Timestamp').reset_index(drop=True)
        
        # Subset data based on selection
        if time_range == "Last 1000 records":
            df = df.tail(1000)
        elif time_range == "Last 500 records":
            df = df.tail(500)
        elif time_range == "Last 200 records":
            df = df.tail(200)
        
        return df
    
    except FileNotFoundError:
        st.error("❌ Error: 'crypto_Currency_data.csv' file not found!")
        st.info("Please upload the cryptocurrency CSV file to continue.")
        return None
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        return None

# --- Mathematical Functions for Simulation ---
def generate_sine_wave(amplitude, frequency, drift, days=365, start_price=1000):
    """Generate price data using sine wave function."""
    t = np.linspace(0, 4*np.pi, days)
    noise = np.random.normal(0, amplitude*0.1, days)
    prices = start_price + amplitude * np.sin(frequency * t) + drift * t + noise
    return prices

# --- Analysis Functions ---
def calculate_volatility(df):
    """Calculate volatility index (standard deviation of returns)."""
    if 'Close Price' in df.columns:
        df['Returns'] = df['Close Price'].pct_change()
        volatility = df['Returns'].std() * 100  # Convert to percentage
        return volatility
    return 0

def calculate_drift(df):
    """Calculate average drift (mean of returns)."""
    if 'Close Price' in df.columns:
        df['Returns'] = df['Close Price'].pct_change()
        avg_drift = df['Returns'].mean() * 100  # Convert to percentage
        return avg_drift
    return 0

def identify_volatility_periods(df, window=20):
    """Identify stable vs volatile periods."""
    if 'Close Price' in df.columns:
        df['Rolling_Std'] = df['Close Price'].rolling(window=window).std()
        volatility_threshold = df['Rolling_Std'].quantile(0.75)
        
        df['Period_Type'] = 'Stable'
        df.loc[df['Rolling_Std'] > volatility_threshold, 'Period_Type'] = 'Volatile'
    
    return df

# --- Main Application ---
# Load data
data = load_and_prepare_data()

if data is not None:
    # --- Key Metrics Display ---
    st.subheader("📊 Key Metrics")
    
    volatility_index = calculate_volatility(data)
    avg_drift = calculate_drift(data)
    last_price = data['Close Price'].iloc[-1] if 'Close Price' in data.columns else 0
    first_price = data['Close Price'].iloc[0] if 'Close Price' in data.columns else 0
    period_return = ((last_price - first_price) / first_price) * 100 if first_price > 0 else 0
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Volatility Index", f"{volatility_index:.2f}%", 
              help="Standard deviation of daily returns")
    m2.metric("Average Drift", f"{avg_drift:.2f}%", 
              help="Mean of daily returns")
    m3.metric("Latest Price", f"${last_price:,.2f}")
    m4.metric("Period Return", f"{period_return:.2f}%",
              delta=f"{period_return:.2f}%",
              delta_color="normal")
    
    st.divider()
    
    # --- Stage 5: Visualizations ---
    st.subheader("📈 Visualizations")
    
    # Tab 1: Price Over Time
    tab1, tab2, tab3, tab4 = st.tabs(["Price Over Time", "High vs Low Analysis", 
                                       "Volume Analysis", "Stable vs Volatile Periods"])
    
    with tab1:
        st.write("### Price Over Time")
        
        if mode == "Real Data Analysis":
            # Real Data Line Chart
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=data['Timestamp'],
                y=data['Close Price'],
                mode='lines',
                name='Close Price',
                line=dict(color='#00CFBE', width=2),
                hovertemplate='Date: %{x}<br>Price: $%{y:,.2f}<extra></extra>'
            ))
            
            fig.update_layout(
                title="Bitcoin Price Over Time",
                xaxis_title="Date",
                yaxis_title="Price (USD)",
                template="plotly_dark",
                hovermode='x unified',
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        else:
            # Mathematical Simulation
            st.write("#### Mathematical Simulation: Sine Wave Pattern")
            sim_days = 365
            sim_prices = generate_sine_wave(amplitude, frequency, drift, sim_days)
            sim_dates = [datetime.now() + timedelta(days=i) for i in range(sim_days)]
            
            fig_sim = go.Figure()
            fig_sim.add_trace(go.Scatter(
                x=sim_dates,
                y=sim_prices,
                mode='lines',
                name='Simulated Price',
                line=dict(color='#FF6B6B', width=2),
                hovertemplate='Date: %{x}<br>Price: $%{y:,.2f}<extra></extra>'
            ))
            
            fig_sim.update_layout(
                title=f"Simulated Price Pattern (Sine Wave)<br>"
                      f"Amplitude: {amplitude}, Frequency: {frequency}, Drift: {drift}",
                xaxis_title="Date",
                yaxis_title="Simulated Price (USD)",
                template="plotly_dark",
                hovermode='x unified',
                height=500
            )
            
            st.plotly_chart(fig_sim, use_container_width=True)
            
            # Show mathematical formula
            st.info(f"""
            **Mathematical Formula Used:**  
            Price(t) = Start Price + Amplitude × sin(Frequency × t) + Drift × t + Noise
            
            Where:
            - Amplitude controls swing size: **{amplitude}**
            - Frequency controls swing speed: **{frequency}**
            - Drift controls long-term trend: **{drift}**
            - Noise is random variation (Gaussian)
            """)
    
    with tab2:
        st.write("### High vs Low Comparison")
        
        fig_hl = go.Figure()
        fig_hl.add_trace(go.Scatter(
            x=data['Timestamp'],
            y=data['High Price'],
            mode='lines',
            name='High Price',
            line=dict(color='#00FF00', width=1),
            hovertemplate='Date: %{x}<br>High: $%{y:,.2f}<extra></extra>'
        ))
        fig_hl.add_trace(go.Scatter(
            x=data['Timestamp'],
            y=data['Low Price'],
            mode='lines',
            name='Low Price',
            line=dict(color='#FF0000', width=1),
            hovertemplate='Date: %{x}<br>Low: $%{y:,.2f}<extra></extra>'
        ))
        
        fig_hl.update_layout(
            title="High vs Low Price Comparison",
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            template="plotly_dark",
            hovermode='x unified',
            height=500
        )
        
        st.plotly_chart(fig_hl, use_container_width=True)
        
        # Calculate daily range
        data['Daily_Range'] = data['High Price'] - data['Low Price']
        avg_range = data['Daily_Range'].mean()
        max_range = data['Daily_Range'].max()
        
        col1, col2 = st.columns(2)
        col1.metric("Average Daily Range", f"${avg_range:,.2f}")
        col2.metric("Maximum Daily Range", f"${max_range:,.2f}")
        
        with st.expander("📊 Daily Range Distribution"):
            fig_range = px.histogram(
                data, 
                x='Daily_Range', 
                nbins=50,
                title="Distribution of Daily Price Ranges",
                template="plotly_dark"
            )
            fig_range.update_layout(xaxis_title="Daily Range (USD)", yaxis_title="Frequency")
            st.plotly_chart(fig_range, use_container_width=True)
    
    with tab3:
        st.write("### Volume Analysis")
        
        # Find volume column
        volume_column = None
        for col in data.columns:
            if 'Volume' in col:
                volume_column = col
                break
        
        if volume_column is None:
            st.warning("Volume column not found in the dataset. Using Close Price instead.")
            volume_column = 'Close Price'
        
        # Volume Bar Chart
        fig_vol = go.Figure()
        fig_vol.add_trace(go.Bar(
            x=data['Timestamp'],
            y=data[volume_column],
            name='Volume',
            marker_color='#00CFBE',
            hovertemplate='Date: %{x}<br>Volume: %{y:,.2f}<extra></extra>'
        ))
        
        volume_label = "BTC" if "BTC" in volume_column else ("USD" if "Currency" in volume_column else "")
        fig_vol.update_layout(
            title="Trading Volume Over Time",
            xaxis_title="Date",
            yaxis_title=f"Volume ({volume_label})",
            template="plotly_dark",
            height=500
        )
        
        st.plotly_chart(fig_vol, use_container_width=True)
        
        # Volume Statistics
        total_volume = data[volume_column].sum()
        avg_volume = data[volume_column].mean()
        max_volume = data[volume_column].max()
        
        v1, v2, v3 = st.columns(3)
        v1.metric("Total Volume", f"{total_volume:,.2f} {volume_label}")
        v2.metric("Average Volume", f"{avg_volume:,.2f} {volume_label}")
        v3.metric("Max Volume", f"{max_volume:,.2f} {volume_label}")
        
        # Correlation Analysis
        st.write("#### Price Change vs Volume Correlation")
        data['Price_Change'] = data['Close Price'].pct_change().abs()
        
        corr_df = data[['Price_Change', volume_column]].dropna()
        correlation = corr_df.corr().iloc[0, 1]
        
        st.metric("Correlation Coefficient", f"{correlation:.4f}",
                 help="Measures relationship between price volatility and trading volume")
        
        fig_corr = px.scatter(
            data,
            x=volume_column,
            y='Price_Change',
            title="Price Change vs Trading Volume",
            template="plotly_dark",
            opacity=0.6
        )
        fig_corr.update_layout(
            xaxis_title=f"Volume ({volume_label})",
            yaxis_title="Price Change (Absolute)"
        )
        st.plotly_chart(fig_corr, use_container_width=True)
    
    with tab4:
        st.write("### Stable vs Volatile Periods")
        
        # Identify periods
        data_with_periods = identify_volatility_periods(data)
        
        # Color periods on chart
        colors = {'Stable': '#00FF00', 'Volatile': '#FF0000'}
        
        fig_periods = go.Figure()
        
        for period_type in ['Stable', 'Volatile']:
            period_data = data_with_periods[data_with_periods['Period_Type'] == period_type]
            fig_periods.add_trace(go.Scatter(
                x=period_data['Timestamp'],
                y=period_data['Close Price'],
                mode='lines',
                name=period_type,
                line=dict(color=colors[period_type], width=1),
                hovertemplate='Date: %{x}<br>Price: $%{y:,.2f}<br>Type: ' + period_type + '<extra></extra>'
            ))
        
        fig_periods.update_layout(
            title="Price Movements: Stable vs Volatile Periods",
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            template="plotly_dark",
            hovermode='x unified',
            height=500
        )
        
        st.plotly_chart(fig_periods, use_container_width=True)
        
        # Period Statistics
        stable_count = (data_with_periods['Period_Type'] == 'Stable').sum()
        volatile_count = (data_with_periods['Period_Type'] == 'Volatile').sum()
        total_count = len(data_with_periods)
        
        p1, p2, p3 = st.columns(3)
        p1.metric("Stable Periods", f"{stable_count} ({stable_count/total_count*100:.1f}%)",
                 delta_color="normal")
        p2.metric("Volatile Periods", f"{volatile_count} ({volatile_count/total_count*100:.1f}%)",
                 delta_color="inverse")
        p3.metric("Threshold", f"${data_with_periods['Rolling_Std'].quantile(0.75):.2f}",
                 help="Rolling standard deviation threshold for volatility classification")
        
        with st.expander("📊 Volatility Rolling Statistics"):
            fig_rolling = go.Figure()
            fig_rolling.add_trace(go.Scatter(
                x=data_with_periods['Timestamp'],
                y=data_with_periods['Rolling_Std'],
                mode='lines',
                name='Rolling Std Dev',
                line=dict(color='#FFA500', width=2)
            ))
            
            # Add threshold line
            threshold = data_with_periods['Rolling_Std'].quantile(0.75)
            fig_rolling.add_hline(
                y=threshold,
                line_dash="dash",
                line_color="red",
                annotation_text=f"Volatile Threshold: {threshold:.2f}"
            )
            
            fig_rolling.update_layout(
                title="Rolling Standard Deviation (Volatility Measure)",
                xaxis_title="Date",
                yaxis_title="Standard Deviation",
                template="plotly_dark",
                height=400
            )
            
            st.plotly_chart(fig_rolling, use_container_width=True)
    
    st.divider()
    
    # --- Explanations and Insights ---
    st.subheader("📝 Analysis Insights")
    
    with st.expander("🔍 Understanding Volatility"):
        st.write("""
        **What is Volatility?**
        Volatility measures how much the price of an asset fluctuates over time. Higher volatility 
        means prices change dramatically in a short period, while lower volatility indicates 
        more stable prices.
        
        **How We Measure It:**
        - **Volatility Index**: Calculated as the standard deviation of daily returns, expressed as a percentage
        - **Rolling Standard Deviation**: Measures volatility over a moving window (20 periods by default)
        - **High vs Low Range**: Shows the daily price range difference
        
        **What This Means for Trading:**
        - **High Volatility**: Greater profit potential but also higher risk
        - **Low Volatility**: More stable but potentially lower returns
        - **Volume Correlation**: High volume during price changes often indicates strong market sentiment
        """)
    
    with st.expander("🎨 Mathematical Models Used"):
        st.write("""
        **1. Sine Wave Model:**
        ```
        Price(t) = Start + Amplitude × sin(Frequency × t) + Drift × t + Noise
        ```
        - Creates smooth, periodic price swings
        - Good for modeling cyclical patterns
        
        **2. Random Noise (Gaussian):**
        - Adds realistic unpredictability
        - Simulates market randomness
        - Based on normal distribution
        
        **3. Drift Component:**
        - Represents long-term trend (bullish or bearish)
        - Positive drift: upward trend
        - Negative drift: downward trend
        """)
    
    st.divider()
    
    # --- Footer ---
    st.caption("Crypto Volatility Visualizer | Mathematics for AI-II | Formative Assessment-2")
    st.caption("Built with Streamlit, Pandas, and Plotly")

else:
    st.warning("⚠️ Please upload 'crypto_Currency_data.csv' to view the dashboard.")
    st.info("""
    **Expected CSV Format:**
    - Timestamp (Unix timestamp)
    - Open, High, Low, Close (prices)
    - Volume (trading volume)
    
    The file should be named exactly: `crypto_Currency_data.csv`
    """)
