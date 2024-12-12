import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import random

import yfinance as yf

# Download historical data for a specific stock
stock = yf.Ticker("TATASTEEL.NS")
data = stock.history(period="1y")  # 1-year data
print(data)
data.to_csv("tata.csv")


# Title
st.title("Interactive Trading Dashboard")

# File Upload
uploaded_file = st.file_uploader("Upload Stock Data (CSV)", type=["csv"])

if uploaded_file:
    # Load stock data
    df = pd.read_csv(uploaded_file)

    # Convert Date column to datetime
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])
    else:
        st.error("The file must contain a 'Date' column.")
        st.stop()

    # Preview data
    st.subheader("Stock Data Preview")
    st.write(df.head())

    # Validate required columns
    required_columns = {'Open', 'High', 'Low', 'Close', 'Volume'}
    if not required_columns.issubset(df.columns):
        st.error(f"The file must contain the following columns: {', '.join(required_columns)}")
        st.stop()

    # Plot Stock Prices with Buy/Sell Signals
    st.subheader("Price Chart with Buy/Sell Signals")
    
    # Simulating Buy/Sell Signals (for demo purposes)
    df['Buy_Signal'] = [random.choice([0, 1]) for _ in range(len(df))]
    df['Sell_Signal'] = [random.choice([0, 1]) for _ in range(len(df))]

    # Create figure
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Close'], mode='lines', name='Stock Price'))
    fig.add_trace(go.Scatter(x=df[df['Buy_Signal'] == 1]['Date'], 
                             y=df[df['Buy_Signal'] == 1]['Close'], 
                             mode='markers', 
                             name='Buy Signal', 
                             marker=dict(color='green', size=10)))
    fig.add_trace(go.Scatter(x=df[df['Sell_Signal'] == 1]['Date'], 
                             y=df[df['Sell_Signal'] == 1]['Close'], 
                             mode='markers', 
                             name='Sell Signal', 
                             marker=dict(color='red', size=10)))
    st.plotly_chart(fig)

    # Predicted Trend
    st.subheader("Predicted Trend")
    predicted_trend = random.choice(["Uptrend", "Downtrend", "Neutral"])
    st.write(f"Predicted Trend: {predicted_trend}")

    # Sentiment Scores
    st.subheader("Sentiment Analysis")
    sentiment_score = random.choice(["Positive", "Neutral", "Negative"])
    st.write(f"Sentiment Score: {sentiment_score}")

    # Support and Resistance
    st.subheader("Support and Resistance Levels")
    support_level = df['Low'].min()
    resistance_level = df['High'].max()
    st.write(f"Support Level: {support_level}")
    st.write(f"Resistance Level: {resistance_level}")

    # Add support and resistance lines to the chart
    fig.add_hline(y=support_level, line_color="blue", annotation_text="Support")
    fig.add_hline(y=resistance_level, line_color="orange", annotation_text="Resistance")
    st.plotly_chart(fig)

    # Volume Analysis
    st.subheader("Volume Analysis")
    st.line_chart(df[['Date', 'Volume']].set_index('Date'))
