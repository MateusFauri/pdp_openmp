CXX = g++
CXXFLAGS = -fopenmp 
SRC = k-means.cpp
EXEC = k-means_exec
PYTHON = python3
RESULTS = resultados.txt
OUTFILE = out.txt
DATA_DIR = arquivos_dados

DATA_FILES = pontos_1000.txt pontos_10000.txt pontos_100000.txt pontos_1000000.txt
DATA_PATHS = $(addprefix $(DATA_DIR)/, $(DATA_FILES))

THREADS = 1 2 5 10 20 40
ITERATIONS = 100
CLUSTERS = 5


$(EXEC): $(SRC)
	$(CXX) $(CXXFLAGS) $(SRC) -o $(EXEC)

run: $(EXEC)
	./get_results.sh

plots:
	@echo "Gerando gráficos de clusters e desempenho..."
	$(PYTHON) plot_kmeans.py

clean:
	rm -f $(EXEC) $(RESULTS) $(OUTFILE)

.PHONY: run plots  clean 
