def answer_question(question, df):
    q = question.lower()

    if "best" in q:
        plant = df.groupby("plant")["output_tons"].mean().idxmax()
        return f"{plant} is the best performing plant."

    if "downtime" in q:
        plant = df.groupby("plant")["downtime_hours"].mean().idxmax()
        return f"{plant} has the highest downtime."

    if "total output" in q:
        return f"Total output is {df['output_tons'].sum()} tons."

    if "energy" in q:
        return f"Average energy usage is {round(df['energy_kwh'].mean(),2)} kWh."

    return "Ask about production, downtime, or energy."
