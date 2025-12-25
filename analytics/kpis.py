def calculate_kpis(df):
    return {
        "total_output": int(df["output_tons"].sum()),
        "avg_downtime": round(df["downtime_hours"].mean(), 2),
        "avg_energy": round(df["energy_kwh"].mean(), 2)
    }

def calculate_health_score(df):
    downtime = max(0, 100 - df["downtime_hours"].mean() * 10)
    energy = max(0, 100 - (df["energy_kwh"].mean() / df["energy_kwh"].max()) * 50)
    output = (df["output_tons"].mean() / df["output_tons"].max()) * 100
    return round((downtime + energy + output) / 3, 1)
