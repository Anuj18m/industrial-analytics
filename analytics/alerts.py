def generate_alerts(df):
    """
    Generate threshold-based and anomaly-based alerts
    """
    alerts = []
    
    # Threshold-based alerts
    if df["downtime_hours"].mean() > 6:
        alerts.append("🚨 High downtime detected")
    if df["energy_kwh"].mean() > df["energy_kwh"].median() * 1.2:
        alerts.append("⚠️ High energy usage detected")
    
    # Anomaly detection (simple statistical)
    output_mean = df["output_tons"].mean()
    output_std = df["output_tons"].std()
    
    if output_std > 0:
        anomalies = df[df["output_tons"] > output_mean + 2 * output_std]
        if len(anomalies) > 0:
            alerts.append(f"🔍 {len(anomalies)} anomaly(ies) detected in output")
    
    # Efficiency-based alert
    total_output = df["output_tons"].sum()
    total_energy = df["energy_kwh"].sum()
    total_downtime = df["downtime_hours"].sum()
    
    if (total_energy + total_downtime * 100) > 0:
        efficiency = total_output / (total_energy + total_downtime * 100)
        if efficiency < 0.25:
            alerts.append("⚡ Low efficiency detected")
    
    return alerts
