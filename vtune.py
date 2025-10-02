import re
import pandas as pd
import matplotlib.pyplot as plt
import os

PLOT_DIR = "plots"
os.makedirs(PLOT_DIR, exist_ok=True)

LOG_FILE = "vtune_log.txt"

pattern = re.compile(
    r"Executando\s+(?P<dataset>pontos_\d+\.txt).*?com\s+(?P<threads>\d+)\s+threads.*?"
    r"Elapsed Time:\s+(?P<elapsed>[\d\.]+)s.*?"
    r"CPI Rate:\s+(?P<cpi>[\d\.]+).*?"
    r"Effective Physical Core Utilization.*?(?P<phys_util>[\d\.]+)%.*?"
    r"Effective Logical Core Utilization:\s+(?P<log_util>[\d\.]+)%.*?"
    r"Memory Bound:\s+(?P<mem_bound>[\d\.]+)%", 
    re.S
)

records = []

with open(LOG_FILE, "r") as f:
    log_data = f.read()
    for match in pattern.finditer(log_data):
        records.append({
            "Dataset": match.group("dataset"),
            "Threads": int(match.group("threads")),
            "ElapsedTime(s)": float(match.group("elapsed")),
            "CPI": float(match.group("cpi")),
            "PhysUtil(%)": float(match.group("phys_util")),
            "LogUtil(%)": float(match.group("log_util")),
            "MemoryBound(%)": float(match.group("mem_bound"))
        })

df = pd.DataFrame(records)
df.to_csv("vtune_summary.csv", index=False)
print(df)

plt.figure(figsize=(8,6))
for dataset, subset in df.groupby("Dataset"):
    plt.plot(subset["Threads"], subset["ElapsedTime(s)"], marker="o", label=dataset)

plt.xlabel("Número de Threads")
plt.ylabel("Tempo de Execução (s)")
plt.title("Tempo de Execução vs Threads (VTune)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(PLOT_DIR, "elapsed_time_vs_threads.png"))
plt.close()

# ====== Gráfico 2: Utilização de núcleos físicos vs threads ======
plt.figure(figsize=(8,6))
for dataset, subset in df.groupby("Dataset"):
    plt.plot(subset["Threads"], subset["PhysUtil(%)"], marker="x", label=dataset)

plt.xlabel("Número de Threads")
plt.ylabel("Utilização Núcleos Físicos (%)")
plt.title("Escalabilidade - Núcleos Físicos (VTune)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(PLOT_DIR, "physical_utilization_vs_threads.png"))
plt.close()

print(f"Gráficos salvos na pasta '{PLOT_DIR}/'")
