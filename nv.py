import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator
from ta.volatility import BollingerBands
import numpy as np

# Title and Sidebar
st.title("📈 Comprehensive Stock Dashboard")
st.sidebar.title("Settings")
st.sidebar.markdown("Customize your experience:")

# Stock Ticker Input
st.sidebar.subheader("Fetch Stock Data")
stock_ticker = st.sidebar.text_input("Enter Stock Ticker (e.g., AAPL, TATASTEEL.NS):", "TATASTEEL.NS")

# Upload Section
uploaded_file = st.sidebar.file_uploader("📂Upload Stock Data (CSV)", type=["csv"])

# Initialize DataFrame
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    if 'Datetime' in df.columns:
        df['Datetime'] = pd.to_datetime(df['Datetime'])
    else:
        st.error("The file must contain a 'Datetime' column.")
        st.stop()

    required_columns = {'Open', 'High', 'Low', 'Close', 'Volume'}
    if not required_columns.issubset(df.columns):
        st.error(f"The file must contain the following columns: {', '.join(required_columns)}")
        st.stop()
else:
    stock = yf.Ticker(stock_ticker)
    df = stock.history(period="6mo", interval = "1h")  # Fetch last 6 months' data
    df.reset_index(inplace=True)

# Ensure required columns exist
if {'Open', 'High', 'Low', 'Close', 'Volume'}.issubset(df.columns):
    st.subheader(f"Stock Data for {stock_ticker}")
    st.write(df.tail())

    # Calculate Technical Indicators
    # RSI HistoAlert Strategy
    rsi_period = 13
    rsi = RSIIndicator(close=df['Close'], window=rsi_period)
    df['RSI'] = rsi.rsi()
    df['RSI_Histo'] = (df['RSI'] - 50) * 1.5  # Modify RSI for histogram

    # Generate Buy/Sell Alerts based on RSI Histo
    buy_alert_level = -10
    sell_alert_level = 10
    df['RSI_Buy_Signal'] = df['RSI_Histo'] < buy_alert_level
    df['RSI_Sell_Signal'] = df['RSI_Histo'] > sell_alert_level

    # Call and Put Strategy
    ema_short = 3
    ema_long = 30
    ema1 = EMAIndicator(close=df['Close'], window=ema_short).ema_indicator()
    ema2 = EMAIndicator(close=df['Close'], window=ema_long).ema_indicator()
    avg_price = (df['Open'] + df['High'] + df['Low'] + df['Close']) / 4

    df['EMA1'] = ema1
    df['EMA2'] = ema2
    df['Buy_Signal'] = (ema1 < avg_price) & (ema2 < avg_price) & (ema2 < ema1)
    df['Sell_Signal'] = (ema1 > avg_price) & (ema2 > avg_price) & (ema2 > ema1)

    # Visualize Price and Indicators
    st.subheader("📊Price Chart with Technical Indicators")
    fig = go.Figure()

    # Add stock price
    fig.add_trace(go.Scatter(x=df['Datetime'], y=df['Close'], mode='lines', name='Close Price', line=dict(color='blue')))

    # Add EMA indicators
    fig.add_trace(go.Scatter(x=df['Datetime'], y=df['EMA1'], name="EMA Short", line=dict(color='yellow')))
    fig.add_trace(go.Scatter(x=df['Datetime'], y=df['EMA2'], name="EMA Long", line=dict(color='orange')))

    # Add Buy/Sell Signals
    fig.add_trace(go.Scatter(x=df[df['Buy_Signal']]['Datetime'], y=df[df['Buy_Signal']]['Close'], 
                             mode='markers', name='Buy Signal', marker=dict(color='green', size=10, symbol="triangle-up")))
    fig.add_trace(go.Scatter(x=df[df['Sell_Signal']]['Datetime'], y=df[df['Sell_Signal']]['Close'], 
                             mode='markers', name='Sell Signal', marker=dict(color='red', size=10, symbol="triangle-down")))

    # RSI Histo Alerts
    fig.add_trace(go.Scatter(x=df[df['RSI_Buy_Signal']]['Datetime'], y=df[df['RSI_Buy_Signal']]['Close'], 
                             mode='markers', name='RSI Buy Alert', marker=dict(color='lightgreen', size=8, symbol="star")))
    fig.add_trace(go.Scatter(x=df[df['RSI_Sell_Signal']]['Datetime'], y=df[df['RSI_Sell_Signal']]['Close'], 
                             mode='markers', name='RSI Sell Alert', marker=dict(color='pink', size=8, symbol="star")))

    st.plotly_chart(fig, use_container_width=True)

    # RSI and Histogram Visualization
    with st.expander("📈 RSI and Histogram Analysis"):
        st.subheader("RSI Over Time")
        st.line_chart(df[['Datetime', 'RSI']].set_index('Datetime'))

        st.subheader("RSI Histogram")
        st.bar_chart(df[['Datetime', 'RSI_Histo']].set_index('Datetime'))
        

    # Support and Resistance Levels
    support_level = df['Low'].min()
    resistance_level = df['High'].max()
    st.sidebar.markdown(f"**Support Level:** {support_level:.2f}")
    st.sidebar.markdown(f"**Resistance Level:** {resistance_level:.2f}")


    # Trend Prediction using Linear Regression
    from sklearn.linear_model import LinearRegression

    st.subheader("📈 Trend Prediction")
    df['NumericDate'] = (df['Datetime'] - df['Datetime'].min()).dt.days

    X = df[['NumericDate']]
    y = df['Close']

    model = LinearRegression()
    model.fit(X, y)

    df['Trend'] = model.predict(X)

    # Add trendline to the plot
    fig.add_trace(go.Scatter(x=df['Datetime'], y=df['Trend'], name='Trendline', line=dict(color='purple', dash='dash')))
    st.plotly_chart(fig, use_container_width=True)

    st.write("### Model Coefficients")
    st.write(f"Slope: {model.coef_[0]:.4f}")
    st.write(f"Intercept: {model.intercept_:.4f}")

else:
    st.info("📂 Upload a CSV file or enter a valid stock ticker to begin.")
