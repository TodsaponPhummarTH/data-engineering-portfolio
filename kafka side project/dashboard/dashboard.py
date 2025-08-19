import streamlit as st
import psycopg2
import pandas as pd
from datetime import date, datetime
import os
import time
from dotenv import load_dotenv
import threading

# Streamlit UI setup
st.set_page_config(page_title="IoT Health Dashboard", layout="wide")

# Initialize session state
if 'auto_refresh' not in st.session_state:
    st.session_state.auto_refresh = True
if 'refresh_interval' not in st.session_state:
    st.session_state.refresh_interval = 10

st.title("🩺 IoT Medical Vital Monitor")

# Control panel (stays static - never refreshes)
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.session_state.auto_refresh = st.checkbox("🔄 Auto-refresh", value=st.session_state.auto_refresh)
with col2:
    st.session_state.refresh_interval = st.selectbox("Interval (sec)", [5, 10, 15, 30], index=1)
with col3:
    manual_refresh = st.button("🔄 Refresh Now")

# Load env
load_dotenv("config/.env")

# DB config
DB_HOST = os.getenv("PG_HOST", "localhost")
DB_PORT = os.getenv("PG_PORT", "5432")
DB_NAME = os.getenv("PG_DB", "airflow")
DB_USER = os.getenv("PG_USER", "airflow")
DB_PASS = os.getenv("PG_PASS", "airflow")

# DB connection function
def get_data():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        today = date.today()
        query = """
            SELECT * FROM iot_readings
            WHERE DATE(timestamp) = %s
            ORDER BY timestamp DESC
            LIMIT 1000;
        """
        df = pd.read_sql(query, conn, params=[today])
        conn.close()
        return df, None
    except Exception as e:
        return pd.DataFrame(), str(e)

# Create empty containers (picture frames that stay in place)
status_container = st.empty()
sidebar_container = st.sidebar.empty()
metrics_container = st.empty()
data_container = st.empty()
chart_container = st.empty()
progress_container = st.empty()

def update_dashboard():
    """Updates only the data containers, not the entire page"""
    
    # Update status
    with status_container.container():
        st.caption(f"⏱ Last refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Load data
    df, error = get_data()
    
    if error:
        with data_container.container():
            st.error(f"Database connection error: {error}")
        return None
    
    if df.empty:
        with data_container.container():
            st.warning("No data for today.")
        return None
    
    # Update sidebar filters (stays persistent)
    with sidebar_container.container():
        st.header("🔍 Filter")
        
        # Get current filter values from session state or set defaults
        if 'selected_device' not in st.session_state:
            st.session_state.selected_device = "All"
        if 'selected_patient' not in st.session_state:
            st.session_state.selected_patient = "All"
        
        device_options = ["All"] + sorted(df["device_id"].dropna().unique())
        selected_device = st.selectbox("Select Device ID", device_options, 
                                     key="device_filter",
                                     index=device_options.index(st.session_state.selected_device) 
                                     if st.session_state.selected_device in device_options else 0)
        st.session_state.selected_device = selected_device
        
        patient_options = ["All"] + sorted(df["patient_id"].dropna().unique())
        selected_patient = st.selectbox("Select Patient ID", patient_options,
                                      key="patient_filter",
                                      index=patient_options.index(st.session_state.selected_patient)
                                      if st.session_state.selected_patient in patient_options else 0)
        st.session_state.selected_patient = selected_patient
    
    # Apply filters
    filtered_df = df.copy()
    if st.session_state.selected_device != "All":
        filtered_df = filtered_df[filtered_df["device_id"] == st.session_state.selected_device]
    if st.session_state.selected_patient != "All":
        filtered_df = filtered_df[filtered_df["patient_id"] == st.session_state.selected_patient]
    
    # Update metrics
    with metrics_container.container():
        st.header("📊 Today's Overview")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Records", len(filtered_df))
        col2.metric("HR > 120", (filtered_df["heart_rate"] > 120).sum())
        col3.metric("SpO2 < 90", (filtered_df["spo2"] < 90).sum())
        col4.metric("Temp > 37.5°C", (filtered_df["temperature"] > 37.5).sum())
    
    # Update data table
    with data_container.container():
        st.subheader("Recent Vital Readings")
        display_df = filtered_df.sort_values(by="timestamp", ascending=False)[[
            "timestamp", "device_id", "patient_id", "heart_rate", "temperature",
            "spo2", "respiratory_rate", "systolic", "diastolic"
        ]].head(20)  # Show only latest 20 for better performance
        st.dataframe(display_df, use_container_width=True)
    
    # Update chart
    with chart_container.container():
        if st.session_state.selected_patient != "All" and not filtered_df.empty:
            st.subheader(f"📈 Heart Rate Trend for {st.session_state.selected_patient}")
            chart_df = filtered_df.sort_values("timestamp").tail(50)  # Last 50 readings
            st.line_chart(chart_df.set_index("timestamp")["heart_rate"])
        else:
            st.info("Select a specific patient to view heart rate trend.")
    
    return filtered_df

# Initial load
update_dashboard()

# Auto-refresh loop
if st.session_state.auto_refresh:
    # Create a placeholder for the progress bar
    with progress_container.container():
        progress_bar = st.progress(0)
        countdown_text = st.empty()
    
    # Countdown and refresh loop
    for i in range(st.session_state.refresh_interval):
        if not st.session_state.auto_refresh:  # Allow user to stop auto-refresh
            break
            
        remaining = st.session_state.refresh_interval - i
        progress = i / st.session_state.refresh_interval
        
        with progress_container.container():
            progress_bar.progress(progress)
            countdown_text.text(f"Next refresh in {remaining} seconds...")
        
        time.sleep(1)
    
    # Clear progress bar and refresh
    progress_container.empty()
    
    # Refresh the dashboard
    if st.session_state.auto_refresh:
        st.rerun()

# Manual refresh trigger
if manual_refresh:
    update_dashboard()
    st.rerun()

# Add some styling for better appearance
st.markdown("""
<style>
    .stProgress > div > div > div > div {
        background-color: #00ff00;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
        margin: 5px;
    }
</style>
""", unsafe_allow_html=True)