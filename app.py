import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- Configuration ---
st.set_page_config(page_title="Nexus Quant: Strategy Backtester", layout="wide")

# --- Styling ---
st.title("📈 Nexus Quant: Strategy Backtester")
st.markdown("Analyze asset momentum using **Stochastic Modeling** and **Trend-Following Signals**.")

# --- Sidebar: Quantitative Inputs ---
st.sidebar.header("Model Parameters")
model_type = st.sidebar.radio(
    "Stochastic Model",
    ("Geometric Brownian Motion", "Mean Reversion (OU Process)")
)

volatility = st.sidebar.slider("Expected Volatility (σ)", 0.01, 0.50, 0.20)
expected_return = st.sidebar.slider("Expected Annual Return (μ)", -0.50, 0.50, 0.10)
time_steps = st.sidebar.number_input("Simulation Days", value=365)

st.sidebar.divider()
st.sidebar.header("Technical Indicators")
fast_window = st.sidebar.slider("Fast MA Window", 5, 20, 10)
slow_window = st.sidebar.slider("Slow MA Window", 21, 100, 50)

# --- Logic: Price Simulation (GBM) ---
def simulate_gbm(mu, sigma, days, start_price=1000):
    dt = 1/365
    returns = np.exp((mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * np.random.normal(0, 1, days))
    price_path = start_price * np.cumprod(returns)
    return price_path

# --- Logic: Signal Generation ---
def generate_signals(df):
    df['Fast_MA'] = df['Price'].rolling(window=fast_window).mean()
    df['Slow_MA'] = df['Price'].rolling(window=slow_window).mean()
    df['Signal'] = 0
    df.loc[df.index[fast_window:], 'Signal'] = np.where(
        df['Fast_MA'][fast_window:] > df['Slow_MA'][fast_window:], 1, -1
    )
    df['Entry_Exit'] = df['Signal'].diff()
    return df

# --- Main Layout ---
tab1, tab2 = st.tabs(["Forecast Engine", "Market Reality"])

with tab1:
    st.header("Monte Carlo Price Path")
    
    # Generate Data
    prices = simulate_gbm(expected_return, volatility, time_steps)
    dates = [datetime.now() + timedelta(days=i) for i in range(time_steps)]
    sim_df = pd.DataFrame({"Date": dates, "Price": prices})
    
    # Plotting
    fig_sim = go.Figure()
    fig_sim.add_trace(go.Scatter(x=sim_df['Date'], y=sim_df['Price'], name="Predicted Path", line=dict(color='#00CFBE')))
    fig_sim.update_layout(title="Asset Projection (Probabilistic)", template="plotly_dark")
    st.plotly_chart(fig_sim, use_container_width=True)
    
    st.success(f"Simulation Complete. Ending Value: ${prices[-1]:.2f}")

with tab2:
    st.header("Historical Analysis")
    
    @st.cache_data
    def fetch_market_data():
        try:
            # Reusing your file logic with a safety check
            df = pd.read_csv("crypto_Currency_data.csv")
            df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='s')
            df = df.rename(columns={'Close': 'Price'}).tail(1000)
            return df
        except:
            return None

    real_data = fetch_market_data()

    if real_data is not None:
        processed_data = generate_signals(real_data)
        
        # Dashboard Metrics
        m1, m2, m3 = st.columns(3)
        last_price = processed_data['Price'].iloc[-1]
        change = (last_price - processed_data['Price'].iloc[0]) / processed_data['Price'].iloc[0] * 100
        
        m1.metric("Latest Price", f"${last_price:,.2f}")
        m2.metric("Period Return", f"{change:.2f}%")
        m3.metric("Signal Status", "BULLISH" if processed_data['Signal'].iloc[-1] == 1 else "BEARISH")

        # Technical Chart
        fig_tech = go.Figure()
        fig_tech.add_trace(go.Scatter(x=processed_data['Timestamp'], y=processed_data['Price'], name="Price", line=dict(color='white', width=1)))
        fig_tech.add_trace(go.Scatter(x=processed_data['Timestamp'], y=processed_data['Fast_MA'], name=f"{fast_window} MA", line=dict(color='orange')))
        fig_tech.add_trace(go.Scatter(x=processed_data['Timestamp'], y=processed_data['Slow_MA'], name=f"{slow_window} MA", line=dict(color='cyan')))
        
        # Add Buy/Sell Markers
        buys = processed_data[processed_data['Entry_Exit'] == 2]
        sells = processed_data[processed_data['Entry_Exit'] == -2]
        
        fig_tech.add_trace(go.Scatter(x=buys['Timestamp'], y=buys['Price'], mode='markers', name='Buy Signal', marker=dict(symbol='triangle-up', size=12, color='#00ff00')))
        fig_tech.add_trace(go.Scatter(x=sells['Timestamp'], y=sells['Price'], mode='markers', name='Sell Signal', marker=dict(symbol='triangle-down', size=12, color='#ff0000')))

        fig_tech.update_layout(title="Moving Average Convergence Divergence", template="plotly_dark", height=600)
        st.plotly_chart(fig_tech, use_container_width=True)
    else:
        st.warning("Please upload 'crypto_Currency_data.csv' to view historical backtests.")

st.markdown("---")
st.caption("Nexus Quant Framework | Stochastic Modeling v2.1")
