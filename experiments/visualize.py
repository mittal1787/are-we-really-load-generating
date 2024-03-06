import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.read_csv("scaling-wrk2.csv")
df.sort_values(["connections", "threads"], inplace=True)
df.rename(
    columns={"connections": "Connection Count",
             "threads": "Thread Count"}, 
    inplace=True)

sns.lineplot(
    data=df[df["Connection Count"] < 200], 
    x="Connection Count", 
    y="RPS", 
    hue="Thread Count",
    palette="tab10")
plt.title("Wrk2 (Gil Tene) RPS by Connections and Threads")
plt.savefig("wrk2-scaling.png", dpi=300)
plt.show()

df = pd.read_csv("scaling-wrk2-dsb.csv")
df.sort_values(["connections", "threads"], inplace=True)
df.rename(
    columns={"connections": "Connection Count",
             "threads": "Thread Count"}, 
    inplace=True)

sns.lineplot(
    data=df[df["Connection Count"] < 200], 
    x="Connection Count", 
    y="RPS", 
    hue="Thread Count",
    palette="tab10")
plt.title("Wrk2 (DeathStarBench) RPS by Connections and Threads")
plt.savefig("wrk2-dsb-scaling.png", dpi=300)
plt.show()
