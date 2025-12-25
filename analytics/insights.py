def generate_insights(df):
    avg = df["output_tons"].mean()
    plant_avg = df.groupby("plant")["output_tons"].mean()

    best = plant_avg.idxmax()
    worst = plant_avg.idxmin()

    return [
        f"{best} is producing above average.",
        f"{worst} is producing below average."
    ]

def generate_summary(df):
    return f"""
Production Avg: {round(df['output_tons'].mean(),2)} tons
Downtime Avg: {round(df['downtime_hours'].mean(),2)} hrs
Energy Avg: {round(df['energy_kwh'].mean(),2)} kWh
"""
