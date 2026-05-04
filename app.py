import streamlit as st
import time
import sqlite3
from datetime import datetime
import traceback

import pandas as pd

from ingestion.data_loader import fetch_data
from analytics.kpis import calculate_kpis, calculate_health_score
from analytics.insights import generate_insights
from analytics.alerts import generate_alerts
from chatbot.qa_engine import answer_question

from database.init_db import init_db
from database.db import DB_PATH
from database.data_updater import start_updater, update_data_once

# Initialize DB on startup so deploys always create the database first
init_db()

# Insert one row immediately so first load is never empty
if 'initial_data_loaded' not in st.session_state:
    update_data_once()
    st.session_state.initial_data_loaded = True

# Debug the active DB file and confirm the table has rows
conn = sqlite3.connect(DB_PATH)
df_debug = pd.read_sql("SELECT * FROM production_data", conn)
conn.close()
print("DEBUG DB PATH:", DB_PATH)
print("DEBUG ROW COUNT:", len(df_debug))

# Start the embedded data updater once per session
if 'updater_started' not in st.session_state:
    st.session_state.updater_started = False

if not st.session_state.updater_started:
    start_updater(interval=5)
    st.session_state.updater_started = True


# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Industrial Analytics", layout="wide")
st.title("🏭 Industrial Analytics Platform")
st.caption("Live industrial monitoring dashboard")

# ---------------- LIVE SETTINGS ----------------
st.sidebar.header("⚙ Live Settings")

refresh_seconds = st.sidebar.selectbox(
    "Refresh interval (seconds)",
    [5, 10, 15, 30],
    index=1
)

window_minutes = st.sidebar.selectbox(
    "Live window (minutes)",
    [1, 5, 10, 30],
    index=1
)

# ---------------- DATA LOAD (NO CACHE!) ----------------
try:
    df = fetch_data(window_minutes=window_minutes)
except Exception as e:
    st.error(f"❌ Error loading data: {str(e)}")
    df = None

if df is None or df.empty:
    st.warning("Initializing data... showing empty dashboard for now.")

tab1, tab2 = st.tabs(["📊 Dashboard", "💬 Chatbot"])

# ---------------- DASHBOARD ----------------
with tab1:
    st.info("📊 **Dashboard Overview**: Real-time KPIs from the last {} minutes. Efficiency Score = Output / (Energy + Downtime). Anomalies flagged when output > mean + 2σ.".format(window_minutes))
    
    try:
        plants = sorted(df["plant"].dropna().unique().tolist()) if "plant" in df.columns else []
        plant = st.selectbox(
            "Select Plant",
            ["All"] + plants
        )

        fdf = df if plant == "All" else df[df["plant"] == plant]

        if fdf.empty:
            st.warning(f"No data available for {plant if plant != 'All' else 'selected time window'}")
        else:
            kpis = calculate_kpis(fdf)
            health = calculate_health_score(fdf)

            # Display KPIs in two rows
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Output (window)", kpis["total_output"], "tons")
            col2.metric("Avg Downtime (hrs)", kpis["avg_downtime"])
            col3.metric("Health Score", f"{health}/100")

            col4, col5, col6 = st.columns(3)
            col4.metric("Efficiency Score", kpis["efficiency_score"], "↑ Higher is better")
            col5.metric("Avg Energy (kWh)", kpis["avg_energy"])
            trend = kpis["trend"]
            col6.metric(trend["direction"], f"{trend['value']} tons", "5-avg trend")

            st.divider()

            st.subheader("📌 Insights")
            for insight in generate_insights(fdf):
                st.info(insight)

            st.subheader("⚠ Alerts")
            alerts = generate_alerts(fdf)
            if alerts:
                for alert in alerts:
                    st.error(alert)
            else:
                st.success("✅ No active alerts")

            st.subheader("📈 Live Production Trend")
            if len(fdf) > 0 and "output_tons" in fdf.columns:
                trend_df = fdf.groupby("date")["output_tons"].sum().sort_index()
                st.line_chart(trend_df)
            else:
                st.info("Not enough data for trend chart yet.")
            
            st.caption(f"📡 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    except Exception as e:
        st.error(f"❌ Dashboard error: {str(e)}")
        st.info("Refreshing in a moment...")

# ---------------- CHATBOT ----------------
with tab2:
    try:
        st.info("💬 **Ask anything about production, downtime, or energy**")
        
        col_hint1, col_hint2, col_hint3 = st.columns(3)
        col_hint1.caption("✅ Try: 'best plant'")
        col_hint2.caption("✅ Try: 'total output'")
        col_hint3.caption("✅ Try: 'downtime'")
        
        question = st.text_input("Ask about production, downtime, or energy")
        
        if question:
            if df is not None and not df.empty:
                answer = answer_question(question, df)
                st.success(answer)
            else:
                st.warning("No data available. Please wait for data ingestion to complete.")
    except Exception as e:
        st.error(f"❌ Chatbot error: {str(e)}")

# ---------------- AUTO RERUN ----------------
time.sleep(refresh_seconds)
st.rerun()
