import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os

# --- Page Configuration ---
st.set_page_config(
    page_title="Crypto Volatility Visualizer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS Styling ---
def load_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        * {
            font-family: 'Inter', sans-serif;
        }
        
        .main {
            background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
        }
        
        .stApp {
            background-color: #0f0f1a;
        }
        
        h1, h2, h3 {
            color: #ffffff;
            font-weight: 600;
        }
        
        .stMetricValue {
            color: #ffffff;
            font-weight: 600;
        }
        
        .stMetricLabel {
            color: #ffffff;
            font-weight: 400;
        }
        
        .plotly-graph-div {
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        }
        
        div[data-testid="stMetricValue"] {
            color: #ffffff;
            font-weight: 600;
        }
        
        div[data-testid="stMetricLabel"] {
            color: #ffffff;
            font-weight: 400;
        }
    </style>
    """, unsafe_allow_html=True)

load_css()

# --- Header Section ---
st.markdown("""
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 20px; margin-bottom: 25px; box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);">
    <h1 style="color: white; margin: 0; text-align: center; font-size: 2.5em;">
        📈 Crypto Volatility Visualizer
    </h1>
    <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0; text-align: center; font-size: 1.1em;">
        Interactive Dashboard for Volatility Analysis & Mathematical Simulations
    </p>
</div>
""", unsafe_allow_html=True)

# --- Sidebar Styling ---
st.sidebar.markdown("""
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 15px; margin-bottom: 20px;">
    <h2 style="color: white; margin: 0;">🎛️ Dashboard Controls</h2>
</div>
""", unsafe_allow_html=True)

# --- Data Loading ---
@st.cache_data
def load_and_prepare_data():
    """Load and clean cryptocurrency data."""
    try:
        # Try to load the CSV file
        df = pd.read_csv("crypto_Currency_data.csv")
        
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
        
        existing_rename = {k: v for k, v in rename_dict.items() if k in df.columns}
        df = df.rename(columns=existing_rename)
        
        # Handle missing data
        if df.isnull().sum().sum() > 0:
            df = df.dropna()
        
        # Sort by timestamp
        if 'Timestamp' in df.columns:
            df = df.sort_values('Timestamp').reset_index(drop=True)
        
        return df, True
    
    except FileNotFoundError:
        # Generate sample data if file not found
        np.random.seed(42)
        base_price = 45000
        days = 500
        dates = pd.date_range(end=datetime.now(), periods=days)
        
        returns = np.random.normal(0.02, 0.05, days)
        price = base_price * (1 + returns).cumprod()
        
        df = pd.DataFrame({
            'Timestamp': dates,
            'Open': price * (1 - np.random.uniform(0.01, 0.03, days)),
            'High': price * (1 + np.random.uniform(0.01, 0.03, days)),
            'Low': price * (1 - np.random.uniform(0.01, 0.03, days)),
            'Close': price,
            'Volume': np.random.uniform(1000000, 50000000, days)
        })
        
        # Rename columns
        df = df.rename(columns={
            'Close': 'Close Price',
            'Open': 'Open Price',
            'High': 'High Price',
            'Low': 'Low Price',
            'Volume': 'Volume BTC'
        })
        
        return df, False

# Load data
df, data_loaded = load_and_prepare_data()

# --- Sidebar: Time Range Selection ---
st.sidebar.markdown("### 📅 Time Range")

time_range = st.sidebar.selectbox(
    "Select Period",
    ["Last 100 records", "Last 200 records", "Last 500 records", "Full Dataset"],
    index=1,
    help="Choose the time period to analyze"
)

def filter_data(df, time_range):
    if time_range == "Last 100 records":
        return df.tail(100)
    elif time_range == "Last 200 records":
        return df.tail(200)
    elif time_range == "Last 500 records":
        return df.tail(500)
    else:
        return df

df_filtered = filter_data(df, time_range)
time_range_title = time_range.replace("Last", "").strip().replace("records", "").strip()

st.sidebar.markdown("---")

# --- Sidebar: Simulation Controls ---
st.sidebar.markdown("### 🎛️ Simulation Controls")

pattern = st.sidebar.selectbox(
    "🌊 Pattern Type",
    ["Sine Wave", "Cosine Wave", "Random Noise", "Combined"],
    help="Choose the mathematical pattern for simulation"
)

preset = st.sidebar.radio(
    "⚡ Volatility Presets",
    ["Custom", "Stable", "Medium Risk", "High Risk"],
    help="Quick volatility presets"
)

# Set preset values
if preset == "Stable":
    amplitude, frequency = 5, 1
elif preset == "Medium Risk":
    amplitude, frequency = 15, 3
elif preset == "High Risk":
    amplitude, frequency = 30, 6
else: 
    amplitude, frequency = 10, 2

amplitude = st.sidebar.slider(
    "📏 Amplitude (Swing Size)", 
    1, 50, amplitude,
    help="How large the price swings will be"
)

frequency = st.sidebar.slider(
    "⏱️ Frequency (Swing Speed)", 
    1, 10, frequency,
    help="How fast the price swings occur"
)

drift = st.sidebar.slider(
    "📈 Drift (Long-Term Trend)", 
    -5, 5, 0,
    help="Long-term price trend direction"
)

shock_toggle = st.sidebar.checkbox(
    "💥 Add Market Shock",
    help="Simulate sudden market disruptions"
)

compare_mode = st.sidebar.checkbox(
    "🔁 Comparison Mode",
    help="Show stable vs volatile comparison"
)

if st.sidebar.button("🔄 Reset Settings", use_container_width=True):
    st.rerun()

# --- Data Warning ---
if not data_loaded:
    st.warning("⚠️ Using generated sample data. Upload 'crypto_Currency_data.csv' for real market data.")

# --- Key Metrics Section ---
st.markdown("""
<div style="background: rgba(102, 126, 234, 0.15); padding: 20px; border-radius: 15px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2);">
    <h2 style="margin: 0;">📊 Key Market Metrics - {}</h2>
</div>
""".format(time_range_title), unsafe_allow_html=True)

# Calculate metrics
volatility = df_filtered['Close Price'].pct_change().std() * 100
avg_price = df_filtered['Close Price'].mean()
price_change = ((df_filtered['Close Price'].iloc[-1] - df_filtered['Close Price'].iloc[0]) / df_filtered['Close Price'].iloc[0]) * 100

col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Average Price", f"${avg_price:,.2f}", help="Average closing price")
col2.metric("⚡ Volatility Index", f"{volatility:.2f}%", help="Standard deviation of returns")
col3.metric("📈 Price Change", f"{price_change:.2f}%", delta=f"{price_change:.2f}%")
col4.metric("📊 Data Points", f"{len(df_filtered):,}", help="Number of records")

# --- Real Data Visualizations ---
st.markdown("---")
st.markdown("""
<div style="background: rgba(102, 126, 234, 0.15); padding: 20px; border-radius: 15px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2);">
    <h2 style="margin: 0;">📈 Real Market Trends - {}</h2>
</div>
""".format(time_range_title), unsafe_allow_html=True)

col1, col2 = st.columns(2)

# Close Price Chart
fig_close = go.Figure()
fig_close.add_trace(go.Scatter(
    x=df_filtered["Timestamp"],
    y=df_filtered["Close Price"],
    mode='lines',
    name='Close Price',
    line=dict(color='#667eea', width=2),
    fill='tozeroy',
    fillcolor='rgba(102, 126, 234, 0.1)'
))
fig_close.update_layout(
    title=f"Close Price Over Time ({time_range_title})",
    template="plotly_dark",
    hovermode='x unified',
    height=400,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#ffffff')
)
col1.plotly_chart(fig_close, use_container_width=True)

# Volume Chart
volume_column = 'Volume BTC' if 'Volume BTC' in df_filtered.columns else 'Volume'
fig_vol = go.Figure()
fig_vol.add_trace(go.Bar(
    x=df_filtered["Timestamp"],
    y=df_filtered[volume_column],
    name='Volume',
    marker=dict(
        color=df_filtered[volume_column],
        colorscale='Viridis',
        showscale=False
    )
))
fig_vol.update_layout(
    title=f"Trading Volume ({time_range_title})",
    template="plotly_dark",
    hovermode='x unified',
    height=400,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#ffffff')
)
col2.plotly_chart(fig_vol, use_container_width=True)

# High vs Low Chart
st.markdown("---")
st.markdown("""
<div style="background: rgba(118, 75, 162, 0.15); padding: 20px; border-radius: 15px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(118, 75, 162, 0.2);">
    <h2 style="margin: 0;">📉 Daily Volatility Range - {}</h2>
</div>
""".format(time_range_title), unsafe_allow_html=True)

fig_hl = go.Figure()
fig_hl.add_trace(go.Scatter(
    x=df_filtered["Timestamp"],
    y=df_filtered["High Price"],
    mode='lines',
    name='High Price',
    line=dict(color='#00ff88', width=2)
))
fig_hl.add_trace(go.Scatter(
    x=df_filtered["Timestamp"],
    y=df_filtered["Low Price"],
    mode='lines',
    name='Low Price',
    line=dict(color='#ff4444', width=2)
))
fig_hl.update_layout(
    title=f"High vs Low Price Comparison ({time_range_title})",
    template="plotly_dark",
    hovermode='x unified',
    height=400,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#ffffff')
)
st.plotly_chart(fig_hl, use_container_width=True)

# Volatility Index
df_filtered["Volatility_Index"] = df_filtered["High Price"] - df_filtered["Low Price"]

st.markdown("---")
st.markdown("""
<div style="background: rgba(255, 107, 107, 0.15); padding: 20px; border-radius: 15px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(255, 107, 107, 0.2);">
    <h2 style="margin: 0;">⚡ Daily Volatility Index</h2>
</div>
""", unsafe_allow_html=True)

fig_volatility = go.Figure()
fig_volatility.add_trace(go.Scatter(
    x=df_filtered["Timestamp"],
    y=df_filtered["Volatility_Index"],
    mode='lines',
    name='Volatility Index',
    line=dict(color='#ff6b6b', width=2),
    fill='tozeroy',
    fillcolor='rgba(255, 107, 107, 0.1)'
))
fig_volatility.update_layout(
    title=f"Daily Price Range ({time_range_title})",
    template="plotly_dark",
    hovermode='x unified',
    height=400,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#ffffff')
)
st.plotly_chart(fig_volatility, use_container_width=True)

# --- Simulation Section ---
st.markdown("---")
st.markdown("""
<div style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%); padding: 20px; border-radius: 15px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);">
    <h2 style="margin: 0;">🎛️ Volatility Simulation Playground</h2>
</div>
""", unsafe_allow_html=True)

def simulate_price(pattern, amp, freq, drift_val, shock=False):
    t = np.linspace(0, 10, 300)
    
    if pattern == "Sine Wave":
        price = amp * np.sin(freq * t)
    elif pattern == "Cosine Wave":
        price = amp * np.cos(freq * t)
    elif pattern == "Random Noise":
        price = amp * np.random.randn(len(t))
    else:  
        price = amp * (np.sin(freq * t) + 0.5 * np.cos(2 * freq * t))
    
    price = price + drift_val * t
    
    if shock:
        shock_indices = np.random.choice(len(t), size=int(len(t) * 0.1), replace=False)
        price[shock_indices] += np.random.normal(0, amp / 2, len(shock_indices))
    
    return t, price

t, sim_price = simulate_price(pattern, amplitude, frequency, drift, shock_toggle)

# Dynamic color based on volatility
volatility_color = '#00ff88' if amplitude < 10 else '#ffaa00' if amplitude < 25 else '#ff4444'

fig_sim = go.Figure()
fig_sim.add_trace(go.Scatter(
    x=t,
    y=sim_price,
    mode='lines',
    name='Simulated Price',
    line=dict(color=volatility_color, width=2),
    fill='tozeroy',
    fillcolor=f'rgba({int(volatility_color[1:3], 16)}, {int(volatility_color[3:5], 16)}, {int(volatility_color[5:7], 16)}, 0.1)'
))
fig_sim.update_layout(
    title=f"Simulated Market Swing Pattern - {pattern} (Amp: {amplitude}, Freq: {frequency}, Drift: {drift})",
    xaxis_title="Time",
    yaxis_title="Simulated Price",
    template="plotly_dark",
    hovermode='x unified',
    height=400,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#ffffff')
)
st.plotly_chart(fig_sim, use_container_width=True)

# Simulation Metrics
st.markdown("---")
st.markdown("""
<div style="background: rgba(255, 255, 255, 0.05); padding: 20px; border-radius: 15px; margin-bottom: 20px;">
    <h2 style="margin: 0;">📌 Simulation Metrics</h2>
</div>
""", unsafe_allow_html=True)

sim_volatility = np.std(sim_price)

col_m1, col_m2, col_m3 = st.columns(3)
col_m1.metric("💰 Average Price", f"{np.mean(sim_price):.2f}", delta=f"±{np.std(sim_price):.2f}")
col_m2.metric("⚡ Volatility Index", f"{sim_volatility:.2f}", delta_color="normal")
col_m3.metric("📈 Drift Value", f"{drift}", delta="Trend" if drift != 0 else "Neutral")

# Comparison Mode
if compare_mode:
    st.markdown("---")
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(0, 255, 136, 0.2) 0%, rgba(255, 68, 68, 0.2) 100%); padding: 20px; border-radius: 15px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0, 255, 136, 0.3);">
        <h2 style="margin: 0;">🔁 Stable vs Volatile Comparison</h2>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    t1, stable = simulate_price("Sine Wave", 5, 1, 0)
    t2, volatile = simulate_price("Sine Wave", 30, 5, 0, shock=True)

    fig_stable = go.Figure()
    fig_stable.add_trace(go.Scatter(
        x=t1, y=stable,
        mode='lines',
        name='Stable Coin',
        line=dict(color='#00ff88', width=2),
        fill='tozeroy',
        fillcolor='rgba(0, 255, 136, 0.1)'
    ))
    fig_stable.update_layout(
        title="Stable Coin (Low Volatility)",
        template="plotly_dark",
        height=350,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#ffffff')
    )
    c1.plotly_chart(fig_stable, use_container_width=True)

    fig_volatile = go.Figure()
    fig_volatile.add_trace(go.Scatter(
        x=t2, y=volatile,
        mode='lines',
        name='Volatile Coin',
        line=dict(color='#ff4444', width=2),
        fill='tozeroy',
        fillcolor='rgba(255, 68, 68, 0.1)'
    ))
    fig_volatile.update_layout(
        title="Volatile Coin (High Volatility)",
        template="plotly_dark",
        height=350,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#ffffff')
    )
    c2.plotly_chart(fig_volatile, use_container_width=True)

# --- Footer ---
st.markdown("---")
st.markdown("""
<div style="background: rgba(0, 0, 0, 0.3); padding: 20px; border-radius: 15px; text-align: center; margin-top: 30px;">
    <p style="color: #ffffff; margin: 0; font-size: 0.9em;">
        📊 Crypto Volatility Visualizer | Mathematics for AI-II | Formative Assessment-2
    </p>
    <p style="color: rgba(255, 255, 255, 0.6); margin: 5px 0 0 0; font-size: 0.8em;">
        Built with Streamlit, Pandas, Plotly & NumPy
    </p>
</div>
""", unsafe_allow_html=True)
