def generate_alerts(df):
    alerts = []
    if df["downtime_hours"].mean() > 6:
        alerts.append("🚨 High downtime detected")
    if df["energy_kwh"].mean() > df["energy_kwh"].median() * 1.2:
        alerts.append("⚠ High energy usage detected")
    return alerts
