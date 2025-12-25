import streamlit as st
import time

from ingestion.data_loader import fetch_data
from analytics.kpis import calculate_kpis, calculate_health_score
from analytics.insights import generate_insights, generate_summary
from analytics.alerts import generate_alerts
from chatbot.qa_engine import answer_question

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
df = fetch_data(window_minutes=window_minutes)

if df.empty:
    st.warning("Waiting for live data...")
    time.sleep(refresh_seconds)
    st.rerun()

tab1, tab2 = st.tabs(["📊 Dashboard", "💬 Chatbot"])

# ---------------- DASHBOARD ----------------
with tab1:
    plant = st.selectbox(
        "Select Plant",
        ["All"] + sorted(df["plant"].dropna().unique())
    )

    fdf = df if plant == "All" else df[df["plant"] == plant]

    kpis = calculate_kpis(fdf)
    health = calculate_health_score(fdf)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Output (window)", kpis["total_output"])
    c2.metric("Avg Downtime (hrs)", kpis["avg_downtime"])
    c3.metric("Avg Energy (kWh)", kpis["avg_energy"])
    c4.metric("Health Score", f"{health}/100")

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
        st.success("No active alerts")

    st.subheader("📈 Live Production Trend")
    trend_df = fdf.groupby("date")["output_tons"].sum().sort_index()
    st.line_chart(trend_df)

# ---------------- CHATBOT ----------------
with tab2:
    question = st.text_input("Ask about production, downtime, or energy")
    if question:
        st.success(answer_question(question, df))

# ---------------- AUTO RERUN ----------------
time.sleep(refresh_seconds)
st.rerun()
