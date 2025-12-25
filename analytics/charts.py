import matplotlib.pyplot as plt

def plot_avg_production(df):
    avg_prod = df.groupby("plant")["output_tons"].mean()
    avg_prod.plot(kind="bar", title="Average Production by Plant")
    plt.ylabel("Output (tons)")
    plt.tight_layout()
    plt.show()

def plot_avg_downtime(df):
    avg_down = df.groupby("plant")["downtime_hours"].mean()
    avg_down.plot(kind="bar", title="Average Downtime by Plant", color="orange")
    plt.ylabel("Downtime (hours)")
    plt.tight_layout()
    plt.show()
