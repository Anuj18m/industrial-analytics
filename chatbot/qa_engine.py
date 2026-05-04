def answer_question(question, df):
    """Answer user questions with error handling"""
    if df.empty or len(df) == 0:
        return "No data available. Please wait for data to be ingested."
    
    q = question.lower().strip()
    
    try:
        if "best" in q or "highest production" in q:
            if df["plant"].nunique() < 2:
                return f"Average production: {round(df['output_tons'].mean(), 0)} tons."
            plant = df.groupby("plant")["output_tons"].mean().idxmax()
            return f"✅ {plant} is the best performing plant."

        if "downtime" in q:
            if df["plant"].nunique() < 2:
                return f"Average downtime: {round(df['downtime_hours'].mean(), 2)} hours."
            plant = df.groupby("plant")["downtime_hours"].mean().idxmax()
            return f"⚠️ {plant} has the highest downtime: {round(df[df['plant']==plant]['downtime_hours'].mean(), 2)} hrs."

        if "total output" in q or "total production" in q:
            return f"📊 Total output: {int(df['output_tons'].sum())} tons."

        if "energy" in q or "consumption" in q:
            return f"⚡ Average energy usage: {round(df['energy_kwh'].mean(), 2)} kWh."

        return "💬 Try asking about: production, downtime, energy, or best plant."
    except Exception as e:
        return f"Unable to answer right now. Try again."
