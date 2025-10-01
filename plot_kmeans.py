import pandas as pd
import matplotlib.pyplot as plt
import re
import os
import warnings
from glob import glob

warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib")

OUT_DIR = "plots"
os.makedirs(OUT_DIR, exist_ok=True)
DATA_DIR = "out"


def plot_clusters(out_file):
    try:
        with open(out_file, "r") as f:
            lines = f.readlines()

        tempo_line = lines[0].strip()
        tempo = None
        match = re.search(r"([\d.]+)", tempo_line)
        if match:
            tempo = float(match.group(1))

        data_str = "".join(lines[1:])
        matches = re.findall(r"(\d+\.?\d*),\s*(\d+\.?\d*)\s*->\s*(\d+)", data_str)
        if not matches:
            print("Nenhum dado de cluster encontrado em", out_file)
            return None

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

        return tempo

    except Exception as e:
        print(f"Erro ao processar {out_file}: {e}")
        return None


def parse_filename(filename):
    """Extrai pontos e threads do nome do arquivo"""
    base = os.path.basename(filename)
    match = re.match(r"pontos_(\d+)_threads(\d+)\.txt", base)
    if not match:
        return None, None
    pontos, threads = int(match.group(1)), int(match.group(2))
    return pontos, threads


def compute_metrics(df):
    metrics = {}
    for pontos, group in df.groupby("pontos"):
        g = group.sort_values("threads")
        if 1 not in g["threads"].values:
            continue
        t1 = float(g.loc[g["threads"] == 1, "tempo"].iloc[0])
        g["speedup"] = t1 / g["tempo"]
        g["efficiency"] = g["speedup"] / g["threads"]
        metrics[pontos] = g
    return metrics


def plot_speedup_efficiency(metrics):
    for pontos, g in metrics.items():
        safe_name = f"pontos_{pontos}"
        threads = g["threads"].values
        speedup = g["speedup"].values
        efficiency = g["efficiency"].values

        # Speedup
        plt.figure(figsize=(8, 5))
        plt.plot(threads, speedup, "o-", label="Speedup real")
        plt.xlabel("Threads")
        plt.ylabel("Speedup")
        plt.title(f"Speedup - {safe_name}")
        plt.grid(True, linestyle="--", alpha=0.6)
        plt.xticks(threads)
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(OUT_DIR, f"speedup_{safe_name}.png"), dpi=200)
        plt.close()

        # Eficiência
        plt.figure(figsize=(8, 5))
        plt.plot(threads, efficiency, "o-")
        plt.xlabel("Threads")
        plt.ylabel("Eficiência")
        plt.title(f"Eficiência - {safe_name}")
        plt.grid(True, linestyle="--", alpha=0.6)
        plt.xticks(threads)
        plt.ylim(0, 1.05)
        plt.tight_layout()
        plt.savefig(os.path.join(OUT_DIR, f"efficiency_{safe_name}.png"), dpi=200)
        plt.close()

        print(f"[OK] Plots de speedup e eficiência salvos para {safe_name}")


if __name__ == "__main__":
    rows = []

    for out_file in glob(os.path.join(DATA_DIR, "pontos_*_threads*.txt")):
        pontos, threads = parse_filename(out_file)
        if pontos is None:
            continue
        tempo = plot_clusters(out_file)
        if tempo is not None:
            rows.append({"arquivo": out_file, "pontos": pontos, "threads": threads, "tempo": tempo})

    if rows:
        df = pd.DataFrame(rows)
        metrics = compute_metrics(df)
        plot_speedup_efficiency(metrics)
    else:
        print("Nenhum arquivo válido encontrado em 'out/'.")
