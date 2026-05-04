import pandas as pd

def calculate_kpis(df):
    """Calculate all KPIs with error handling"""
    if df.empty or len(df) == 0:
        return {
            "total_output": 0,
            "avg_downtime": 0,
            "avg_energy": 0,
            "efficiency_score": 0,
            "trend": {"direction": "⏳ Waiting", "value": 0}
        }
    
    return {
        "total_output": int(df["output_tons"].sum()),
        "avg_downtime": round(df["downtime_hours"].mean(), 2),
        "avg_energy": round(df["energy_kwh"].mean(), 2),
        "efficiency_score": calculate_efficiency_score(df),
        "trend": calculate_trend(df)
    }

def calculate_efficiency_score(df):
    """
    Efficiency = Output / (Energy + Downtime)
    Higher is better: more output with less energy/downtime waste
    """
    if len(df) == 0:
        return 0
    
    try:
        total_output = df["output_tons"].sum()
        total_energy = df["energy_kwh"].sum()
        total_downtime = df["downtime_hours"].sum()
        
        denominator = total_energy + (total_downtime * 100)
        
        if denominator == 0 or total_output == 0:
            return 0
        
        result = total_output / denominator
        return round(result, 3)
    except Exception:
        return 0


def calculate_trend(df):
    """
    Calculate 5-row moving average for trend detection
    Returns: trend direction and smoothed recent value
    """
    if len(df) < 1:
        return {"direction": "⏳ Waiting", "value": 0}
    
    try:
        df_sorted = df.sort_values("date").reset_index(drop=True)
        window_size = min(5, len(df_sorted))
        
        df_sorted["rolling_avg"] = df_sorted["output_tons"].rolling(window=window_size).mean()
        recent_trend = df_sorted["rolling_avg"].iloc[-1]
        
        if len(df_sorted) >= 2:
            prev_trend = df_sorted["rolling_avg"].iloc[-2]
            if pd.notna(recent_trend) and pd.notna(prev_trend):
                if recent_trend > prev_trend * 1.05:
                    direction = "📈 Uptrend"
                elif recent_trend < prev_trend * 0.95:
                    direction = "📉 Downtrend"
                else:
                    direction = "➡️ Stable"
            else:
                direction = "➡️ Stable"
        else:
            direction = "➡️ Stable"
        
        return {
            "direction": direction,
            "value": round(float(recent_trend), 1) if pd.notna(recent_trend) else 0
        }
    except Exception:
        return {"direction": "➡️ Stable", "value": 0}

def calculate_health_score(df):
    """Calculate composite health score with error handling"""
    if len(df) == 0:
        return 0
    
    try:
        downtime = max(0, 100 - df["downtime_hours"].mean() * 10)
        
        max_energy = df["energy_kwh"].max()
        energy = max(0, 100 - (df["energy_kwh"].mean() / max_energy * 50)) if max_energy > 0 else 50
        
        max_output = df["output_tons"].max()
        output = (df["output_tons"].mean() / max_output * 100) if max_output > 0 else 50
        
        health = (downtime + energy + output) / 3
        return round(health, 1)
    except Exception:
        return 50  # Default middle score
