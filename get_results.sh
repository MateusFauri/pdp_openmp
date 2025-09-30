#!/bin/bash

EXEC="./k-means_exec"
DATA_DIR="./arquivos_dados"
OUT_DIR="./out"
VTUNE_OUT="./vtune_out"
RESULT_FILE="execution_times.txt"
ITERATIONS=100
CLUSTERS=5

DATA_FILES=("pontos_10.txt" "pontos_100.txt" "pontos_1000.txt" "pontos_10000.txt" "pontos_100000.txt" "pontos_1000000.txt")

NUM_THREADS_LIST=(1 2 5 10 20 40)

mkdir -p $OUT_DIR
mkdir -p $VTUNE_OUT

echo "Arquivo Num_Pontos Threads Tempo(s)" > "$RESULT_FILE"

# Checa se VTune está ativo
if [ -z "$VTUNE_ACTIVE" ]; then
    VTUNE_ACTIVE=0
else
    VTUNE_ACTIVE=1
fi
echo "VTune active: $VTUNE_ACTIVE"

overall_start=$(date +%s.%N)

for t in "${NUM_THREADS_LIST[@]}"; do
    export OMP_NUM_THREADS=$t
    echo "=== Testando com OMP_NUM_THREADS=$t ==="

    for f in "${DATA_FILES[@]}"; do
        FILE_PATH="$DATA_DIR/$f"
        if [ ! -f "$FILE_PATH" ]; then
            echo "AVISO: Arquivo $FILE_PATH não encontrado, pulando..."
            continue
        fi

        NUM_PONTOS=$(echo "$f" | cut -d'_' -f2 | cut -d'.' -f1)
        OUT_FILE="$OUT_DIR/${f%.txt}_threads${t}.txt"

        echo "Executando $f com $t threads..."

        start_time=$(date +%s.%N)

        if [ $VTUNE_ACTIVE -eq 1 ]; then
            VTUNE_OUTPUT="$VTUNE_OUT/vtune_${f%.txt}_threads${t}"
            vtune -collect hpc-performance -r $VTUNE_OUTPUT $EXEC $ITERATIONS $CLUSTERS $FILE_PATH &> $OUT_FILE
        else
            $EXEC $ITERATIONS $CLUSTERS $FILE_PATH &> $OUT_FILE
        fi

        ext_code=$?
        end_time=$(date +%s.%N)

        if [ -f "$OUT_FILE" ]; then
            TEMPO=$(head -n1 "$OUT_FILE" | awk '{print $NF}')
        else
            TEMPO="ERRO"
        fi

        echo "$f $NUM_PONTOS $t $TEMPO" >> "$RESULT_FILE"
        elapsed=$(echo "$end_time - $overall_start" | bc)
        echo "Tempo decorrido: $elapsed s, exit code: $ext_code"
    done
done

echo "Resultados salvos em $RESULT_FILE"
total_elapsed=$(echo "$(date +%s.%N) - $overall_start" | bc)
echo "Tempo total de execução: $total_elapsed s"
