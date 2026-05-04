def generate_insights(df):
    """Generate insights with proper error handling for empty/single-plant data"""
    if df.empty or len(df) == 0:
        return ["No data available for insights."]
    
    if "plant" not in df.columns or df["plant"].nunique() < 2:
        avg = df["output_tons"].mean()
        return [f"Average production: {round(avg, 0)} tons."]
    
    try:
        avg = df["output_tons"].mean()
        plant_avg = df.groupby("plant")["output_tons"].mean()
        
        best = plant_avg.idxmax()
        worst = plant_avg.idxmin()
        
        return [
            f"✅ {best} is producing above average.",
            f"⚠️ {worst} is producing below average."
        ]
    except Exception:
        return ["Unable to generate insights at this time."]

def generate_summary(df):
    """Generate summary with error handling"""
    if df.empty:
        return "No data available."
    
    return f"""
Production Avg: {round(df['output_tons'].mean(), 2)} tons
Downtime Avg: {round(df['downtime_hours'].mean(), 2)} hrs
Energy Avg: {round(df['energy_kwh'].mean(), 2)} kWh
"""
