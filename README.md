# 1000409-Mohammed-saif-Crypto-Volatility
Crypto Volatility Visualizer

A comprehensive Streamlit dashboard for analyzing cryptocurrency volatility using mathematical models and real market data. This project is built as part of the Mathematics for AI-II course (Formative Assessment-2).

App link: https://1000409-mohammed-saif-crypto-volatility-doacfl9e5sneisrgappnsu.streamlit.app/ 


🎯 Project Overview

This dashboard allows users to:

- Analyze real cryptocurrency market data

- Simulate price movements using mathematical functions (sine/cosine waves)

- Visualize volatility patterns with interactive charts

- Compare stable vs volatile trading periods

- Understand market behavior through key metrics

📊 Features

Data Analysis

- Real-time cryptocurrency data visualization

- High vs Low price comparison charts

- Volume analysis with correlation studies

- Stable vs Volatile period identification

- Robust column name handling for different CSV formats

Mathematical Simulation

- Sine wave pattern simulation

- Adjustable parameters (amplitude, frequency, drift)

- Random noise injection for realism

- Mathematical formula explanations

Interactive Controls

- Sidebar parameter adjustments

- Time range selection

- Real-time chart updates

- Responsive design


🎨 Dashboard Sections

1. Key Metrics

- Volatility Index: Standard deviation of daily returns

- Average Drift: Mean of daily returns

- Latest Price: Current closing price

- Period Return: Total return over the selected period

2. Price Over Time

- Line chart showing price movements

- Toggle between real data and mathematical simulation

- Interactive hover for detailed information

3. High vs Low Analysis

- Comparison of daily high and low prices

- Daily range distribution histogram

- Average and maximum daily range metrics

4. Volume Analysis

- Trading volume bar chart

- Volume statistics (total, average, max)

- Price change vs volume correlation scatter plot

5. Stable vs Volatile Periods

- Color-coded price movements

- Period statistics (stable vs volatile counts)

- Rolling standard deviation chart with threshold

🔧 Configuration

Sidebar Controls

- Analysis Mode: Choose between "Real Data Analysis" and "Mathematical Simulation"

- Simulation Parameters:

- Amplitude: Controls swing size (10-500)

- Frequency: Controls swing speed (0.1-5.0)

- Drift: Controls long-term trend (-2.0 to 2.0)

- Data Range: Select time period (Last 1000/500/200 records or All data)

📊 Mathematical Models

Sine Wave Model

Price(t) = Start + Amplitude × sin(Frequency × t) + Drift × t + Noise

Where:

- Amplitude: Magnitude of price swings

- Frequency: How often swings occur

- Drift: Long-term upward/downward trend

- Noise: Random variation (Gaussian)

Volatility Calculation

- Standard Deviation: Measures price dispersion

- Rolling Std Dev: Moving window volatility

- Returns: Percentage change between periods


📖 References

- Streamlit Documentation

- Plotly Python Documentation

- Pandas Documentation

- DataCamp Streamlit Tutorial


Course: Mathematics for AI-II
Assessment: Formative Assessment-2
Institution: FinTechLab Pvt. Ltd.
Date: 2024
