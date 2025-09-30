import pandas as pd
import matplotlib.pyplot as plt
import re
import os
import warnings
import numpy as np

warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib")

RESULT_FILE = "resultados.txt"
OUT_DIR = "plots"
os.makedirs(OUT_DIR, exist_ok=True)


def plot_clusters(out_file):
    try:
        with open(out_file, "r") as f:
            next(f)
            data_str = f.read()

        matches = re.findall(r"(\d+\.?\d*),\s*(\d+\.?\d*)\s*->\s*(\d+)", data_str)
        if not matches:
            print("Nenhum dado de cluster encontrado em", out_file)
            return

        data = pd.DataFrame(matches, columns=["x", "y", "cluster"])
        data = data.apply(pd.to_numeric)

        plt.figure(figsize=(10, 7))
        for cluster_id in sorted(data["cluster"].unique()):
            cluster_data = data[data["cluster"] == cluster_id]
            plt.scatter(
                cluster_data["x"],
                cluster_data["y"],
                label=f"Cluster {cluster_id}",
                alpha=0.7,
                s=40,
            )
        plt.xlabel("X")
        plt.ylabel("Y")
        plt.title(f"Clusters - {os.path.basename(out_file)}")
        plt.legend()
        plt.grid(True, linestyle="--", alpha=0.6)
        plt.tight_layout()
        plt.savefig(
            os.path.join(
                OUT_DIR, f"clusters_{os.path.basename(out_file).replace('.txt','')}.png"
            ),
            dpi=200,
        )
        plt.close()
        print(f"[OK] Gráfico de clusters salvo para {out_file}")

    except Exception as e:
        print(f"Erro ao processar {out_file}: {e}")


def read_results(result_file):
    rows = []
    with open(result_file, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("-"):
                continue
            parts = [p.strip() for p in line.split("|")]
            if len(parts) != 4:
                continue
            nome, pontos, threads, tempo = parts
            pontos = int(pontos.replace(",", ""))
            threads = int(threads)
            try:
                tempo = float(tempo)
            except:
                continue
            rows.append(
                {"arquivo": nome, "pontos": pontos, "threads": threads, "tempo": tempo}
            )
    return pd.DataFrame(rows)


def compute_metrics(df):
    metrics = {}
    for nome, group in df.groupby("arquivo"):
        g = group.sort_values("threads")
        if 1 not in g["threads"].values:
            continue
        t1 = float(g.loc[g["threads"] == 1, "tempo"].iloc[0])
        g["speedup"] = t1 / g["tempo"]
        g["efficiency"] = g["speedup"] / g["threads"]
        metrics[nome] = g
    return metrics


def plot_speedup_efficiency(metrics):
    for nome, g in metrics.items():
        safe_name = nome.replace(".txt", "").replace("/", "_")
        threads = g["threads"].values
        speedup = g["speedup"].values
        efficiency = g["efficiency"].values

        # Speedup
        plt.figure(figsize=(8, 5))
        plt.plot(threads, speedup, "o-", label="Speedup real")
        plt.xlabel("Threads")
        plt.ylabel("Speedup")
        plt.title(f"Speedup - {nome}")
        plt.grid(True, linestyle="--", alpha=0.6)
        plt.xticks(threads)
        plt.ylim(0, 5)
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(OUT_DIR, f"speedup_{safe_name}.png"), dpi=200)
        plt.close()

        # Eficiência
        plt.figure(figsize=(8, 5))
        plt.plot(threads, efficiency, "o-")
        plt.xlabel("Threads")
        plt.ylabel("Eficiência")
        plt.title(f"Eficiência - {nome}")
        plt.grid(True, linestyle="--", alpha=0.6)
        plt.xticks(threads)
        plt.ylim(0, 1.05)
        plt.tight_layout()
        plt.savefig(os.path.join(OUT_DIR, f"efficiency_{safe_name}.png"), dpi=200)
        plt.close()

        print(f"[OK] Plots de speedup e eficiência salvos para {nome}")


if __name__ == "__main__":
    if os.path.exists("out.txt"):
        plot_clusters("out.txt")
    else:
        print("Arquivo out.txt não encontrado, pulando gráfico de clusters.")

    if os.path.exists(RESULT_FILE):
        df = read_results(RESULT_FILE)
        metrics = compute_metrics(df)
        plot_speedup_efficiency(metrics)
    else:
        print(
            f"Arquivo {RESULT_FILE} não encontrado, pulando gráficos de speedup/eficiência."
        )
