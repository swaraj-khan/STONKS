import pandas as pd
import numpy as np
import streamlit as st
import time
from threading import Thread

data = pd.read_excel("yahoo_data.xlsx")
data['Date'] = pd.to_datetime(data['Date'])
data.set_index('Date', inplace=True)
data = data.resample('1T').mean().dropna()  
data = data[['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']].tail(1000)  

tick_data = []
swing_highs = []
swing_lows = []
highest_peak = None
lowest_depth = None
simulation_running = False

def simulate_ticks():
    global tick_data, simulation_running
    while simulation_running:
        current_time = pd.Timestamp.now()
        if current_time in data.index:
            tick_data.append(data.loc[current_time].tolist())
        else:
            last_tick = tick_data[-1] if tick_data else [current_time, 0, 0, 0, 0, 0]
            tick_data.append([
                current_time,
                last_tick[1] + np.random.randn() * 0.1,  
                last_tick[2] + np.random.randn() * 0.1,  
                last_tick[3] + np.random.randn() * 0.1,  
                last_tick[4] + np.random.randn() * 0.1,  
                np.random.randint(1000)  
            ])
        time.sleep(1)

def calculate_swing_points():
    global swing_highs, swing_lows, highest_peak, lowest_depth
    if len(tick_data) >= 3:
        last_tick = tick_data[-1][4]  
        previous_tick = tick_data[-2][4]
        before_previous_tick = tick_data[-3][4]

        if last_tick > previous_tick and previous_tick > before_previous_tick:
            swing_highs.append(tick_data[-2])
        elif last_tick < previous_tick and previous_tick < before_previous_tick:
            swing_lows.append(tick_data[-2])
        
        current_high = max(tick_data[-5:], key=lambda x: x[2])[2]  
        current_low = min(tick_data[-5:], key=lambda x: x[3])[3]   
        
        highest_peak = current_high
        lowest_depth = current_low

def start_simulation():
    global simulation_running
    simulation_running = True
    simulate_ticks()

st.title("TradingView Demo with Real-time Data")

if st.button("Start Simulation"):
    st.write("Simulation started...")
    Thread(target=start_simulation, daemon=True).start()

if st.button("Stop Simulation"):
    st.write("Simulation stopped.")
    simulation_running = False

chart = st.line_chart([], use_container_width=True)

while True:
    if tick_data:
        calculate_swing_points()
        
        df = pd.DataFrame(tick_data, columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
        
        chart.line_chart(df.set_index('Date')['Close'])

        if swing_highs:
            last_swing_high = swing_highs[-1][4]  
            st.write(f"Swing High: {last_swing_high} at {swing_highs[-1][0]}")  
            
        if swing_lows:
            last_swing_low = swing_lows[-1][4]  
            st.write(f"Swing Low: {last_swing_low} at {swing_lows[-1][0]}")  

        if highest_peak is not None and lowest_depth is not None:
            st.markdown(f"**Highest Peak:** <span style='color:green;'>{highest_peak}</span>", unsafe_allow_html=True)
            st.markdown(f"**Lowest Depth:** <span style='color:red;'>{lowest_depth}</span>", unsafe_allow_html=True)

        st.write("---")

    time.sleep(1)
