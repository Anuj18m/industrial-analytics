# Industrial Analytics Dashboard

[![Live App](https://img.shields.io/badge/Live%20App-Open-green?style=flat-square)](https://industrial-analytics-algoonerd.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.x-blue?style=flat-square)]()
[![Streamlit](https://img.shields.io/badge/Framework-Streamlit-red?style=flat-square)]()
[![SQLite](https://img.shields.io/badge/Database-SQLite-lightgrey?style=flat-square)]()

📊 Real-time industrial analytics system focused on **data pipelines, not just dashboards**

---

## Overview

This project simulates a real-world industrial monitoring system where production data is continuously ingested, processed, and analyzed in real time.

Instead of focusing only on visualization, the system is designed around:

* reliable data ingestion
* consistent metric computation
* stable system behavior under continuous updates

---

## Core Capabilities

* ⚙️ Continuous data ingestion using a background thread
* 📈 Real-time KPI computation (output, downtime, energy, efficiency)
* 🚨 Anomaly detection using statistical thresholds
* 🖥️ Interactive monitoring dashboard
* 💬 Rule-based query interface for quick insights

---

## System Design

```text id="m0e6xf"
Streamlit UI
   ↓
Analytics Layer (KPIs, Alerts, Insights)
   ↓
Background Data Updater
   ↓
SQLite Database
```

---

## Engineering Highlights

* 🔄 Non-blocking ingestion architecture using daemon threads
* 🧠 Safe database initialization (no table drops, no race conditions)
* 📊 Sliding window analytics for consistent real-time metrics
* 🧩 Modular design separating ingestion, analytics, and UI
* ⚡ Deployment-ready (handles cold start, threading, and DB sync issues)

---

## Demo

![Dashboard](screenshots/dashboard_kpis_overview.png)
![Analytics](screenshots/dashboard_insights_alerts.png)
![Chatbot](screenshots/chatbot_query_response.png)


🚀 **Live Demo:** https://industrial-analytics-algoonerd.streamlit.app/

📂 **Repository:** https://github.com/Anuj18m/industrial-analytics

---

## Running Locally

```bash id="c3c0p9"
pip install -r requirements.txt
streamlit run app.py
```

---

## Project Structure

```text id="8k0x9l"
industrial-analytics/
├── app.py
├── analytics/
├── database/
├── ingestion/
├── chatbot/
├── data/
└── screenshots/
```

---

## Future Scope

* 🤖 ML-based anomaly detection
* 🏭 Multi-plant comparative analytics
* 🗄️ Migration to PostgreSQL
* 🔐 Authentication & role-based access

---

## Author

**Anuj Mhatre**
🔗 https://linkedin.com/in/anujmhatre17
