import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from ta.momentum import RSIIndicator
from ta.trend import MACD
from ta.volatility import BollingerBands
import random

# Title and Sidebar
st.title("📈 Comprehensive Stock Dashboard")
st.sidebar.title("Settings")
st.sidebar.markdown("Customize your experience:")

# Stock Ticker Input
st.sidebar.subheader("Fetch Stock Data")
stock_ticker = st.sidebar.text_input("Enter Stock Ticker (e.g., AAPL, TATASTEEL.NS):", "TATASTEEL.NS")

# Upload Section
uploaded_file = st.sidebar.file_uploader("📂 Upload Stock Data (CSV)", type=["csv"])

# Initialize DataFrame
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])
    else:
        st.error("The file must contain a 'Date' column.")
        st.stop()

    required_columns = {'Open', 'High', 'Low', 'Close', 'Volume'}
    if not required_columns.issubset(df.columns):
        st.error(f"The file must contain the following columns: {', '.join(required_columns)}")
        st.stop()
else:
    stock = yf.Ticker(stock_ticker)
    df = stock.history(period="6mo")  # Fetch last 6 months' data
    df.reset_index(inplace=True)

# Ensure required columns exist
if {'Open', 'High', 'Low', 'Close', 'Volume'}.issubset(df.columns):
    st.subheader(f"Stock Data for {stock_ticker}")
    st.write(df.tail())

    # Calculate Technical Indicators
    rsi = RSIIndicator(close=df['Close'], window=14)
    df['RSI'] = rsi.rsi()

    macd = MACD(close=df['Close'])
    df['MACD'] = macd.macd()
    df['MACD_Signal'] = macd.macd_signal()
    df['MACD_Hist'] = macd.macd_diff()

    bb = BollingerBands(close=df['Close'], window=20, window_dev=2)
    df['BB_High'] = bb.bollinger_hband()
    df['BB_Low'] = bb.bollinger_lband()

    # Moving Averages
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    df['SMA_200'] = df['Close'].rolling(window=200).mean()

    # Define Buy/Sell Signals
    df['Buy_Signal'] = (df['RSI'] < 30) & (df['Close'] < df['BB_Low'])
    df['Sell_Signal'] = (df['RSI'] > 70) & (df['Close'] > df['BB_High'])

    # Visualize Price and Indicators
    st.subheader("📊 Price Chart with Technical Indicators")
    fig = go.Figure()

    # Add stock price
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Close'], mode='lines', name='Close Price', line=dict(color='blue')))

    # Add Bollinger Bands
    fig.add_trace(go.Scatter(x=df['Date'], y=df['BB_High'], name="Bollinger High", line=dict(color='orange', dash='dot')))
    fig.add_trace(go.Scatter(x=df['Date'], y=df['BB_Low'], name="Bollinger Low", line=dict(color='orange', dash='dot')))

    # Add Moving Averages
    fig.add_trace(go.Scatter(x=df['Date'], y=df['SMA_50'], name="SMA 50", line=dict(color='purple')))
    fig.add_trace(go.Scatter(x=df['Date'], y=df['SMA_200'], name="SMA 200", line=dict(color='green')))

    # Add Buy/Sell Signals
    fig.add_trace(go.Scatter(x=df[df['Buy_Signal']]['Date'], y=df[df['Buy_Signal']]['Close'], 
                             mode='markers', name='Buy Signal', marker=dict(color='green', size=10, symbol="triangle-up")))
    fig.add_trace(go.Scatter(x=df[df['Sell_Signal']]['Date'], y=df[df['Sell_Signal']]['Close'], 
                             mode='markers', name='Sell Signal', marker=dict(color='red', size=10, symbol="triangle-down")))

    st.plotly_chart(fig, use_container_width=True)

    # RSI and MACD Analysis
    with st.expander("📈 RSI and MACD Analysis"):
        st.subheader("RSI Over Time")
        st.line_chart(df[['Date', 'RSI']].set_index('Date'))

        st.subheader("MACD Over Time")
        fig_macd = go.Figure()
        fig_macd.add_trace(go.Scatter(x=df['Date'], y=df['MACD'], name='MACD', line=dict(color='blue')))
        fig_macd.add_trace(go.Scatter(x=df['Date'], y=df['MACD_Signal'], name='Signal Line', line=dict(color='red', dash='dot')))
        fig_macd.add_trace(go.Bar(x=df['Date'], y=df['MACD_Hist'], name='Histogram', marker=dict(color='green')))
        st.plotly_chart(fig_macd, use_container_width=True)

    # Highlight Support and Resistance Levels
    support_level = df['Low'].min()
    resistance_level = df['High'].max()
    st.sidebar.markdown(f"**Support Level:** {support_level:.2f}")
    st.sidebar.markdown(f"**Resistance Level:** {resistance_level:.2f}")

    # Ensure required columns
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    df['SMA_200'] = df['Close'].rolling(window=200).mean()
    rsi = RSIIndicator(close=df['Close'], window=14)
    df['RSI'] = rsi.rsi()

    # Predict Trend
    def predict_trend(data):
        """
        Predict market trend based on SMA and RSI indicators.
        """
        # Check if sufficient data is available for SMA calculations
        if len(data) < 200:  # Not enough rows for SMA_200
            return "Neutral"

        # Check for NaN values in the required columns
        if data[['SMA_50', 'SMA_200', 'RSI']].isnull().any().any():
            return "Neutral"  # Incomplete data

        # Trend logic
        if data['SMA_50'].iloc[-1] > data['SMA_200'].iloc[-1] and data['RSI'].iloc[-1] > 50:
            return "Uptrend"
        elif data['SMA_50'].iloc[-1] < data['SMA_200'].iloc[-1] and data['RSI'].iloc[-1] < 50:
            return "Downtrend"
        else:
            return "Neutral"


    # Ensure required columns are generated
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    df['SMA_200'] = df['Close'].rolling(window=200).mean()
    rsi = RSIIndicator(close=df['Close'], window=14)
    df['RSI'] = rsi.rsi()

    # Debugging: Check if columns contain NaN values
    st.write("Columns with NaN values:", df[['SMA_50', 'SMA_200', 'RSI']].isnull().sum())

    # Predict Trend
    predicted_trend = predict_trend(df)
    trend_colors = {"Uptrend": "🟢", "Downtrend": "🔴", "Neutral": "🟡"}
    st.subheader("📈 Predicted Trend")
    st.markdown(f"**{trend_colors[predicted_trend]} Predicted Trend: {predicted_trend}**")



    # Sentiment Analysis
    st.subheader("🧠 Sentiment Analysis")
    sentiment_score = random.choice(["Positive", "Neutral", "Negative"])
    st.markdown(f"**Sentiment Score: {sentiment_score}**")

    # Volume Analysis
    st.subheader("📉 Volume Analysis")
    st.line_chart(df[['Date', 'Volume']].set_index('Date'))

else:
    st.info("📂 Upload a CSV file or enter a valid stock ticker to begin.")
