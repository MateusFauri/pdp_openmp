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


# Compila o programa C++
$(EXEC): $(SRC)
	@echo "Compilando $(SRC) com OpenMP..."
	$(CXX) $(CXXFLAGS) $(SRC) -o $(EXEC)
	@echo "Executável $(EXEC) criado com sucesso!"

# Executa todos os testes 
run: $(EXEC)
	@echo "Executando testes do K-Means..."
	@echo "# Resultados de Tempo de Execução do K-Means Paralelizado" > $(RESULTS)
	@echo "# Iterações = $(ITERATIONS), Clusters = $(CLUSTERS)" >> $(RESULTS)
	@echo "# Arquivos de dados: $(DATA_DIR)" >> $(RESULTS)
	@echo "# Formato: Nome_Arquivo | Numero_de_Pontos | Numero_de_Threads | Tempo (s)" >> $(RESULTS)
	@echo "----------------------------------------------------------------------------------------------------------------------" >> $(RESULTS)
	@for t in $(THREADS); do \
		echo "=== Testando com OMP_NUM_THREADS=$$t ==="; \
		export OMP_NUM_THREADS=$$t; \
		for f in $(DATA_PATHS); do \
			if [ ! -f $$f ]; then echo "AVISO: Arquivo $$f não encontrado, pulando..."; continue; fi; \
			NUM_PONTOS=$$(basename $$f | cut -d'_' -f2 | cut -d'.' -f1); \
			echo "Executando $$f..."; \
			./$(EXEC) $(ITERATIONS) $(CLUSTERS) $$f; \
			if [ -f $(OUTFILE) ]; then \
				TEMPO=$$(head -n1 $(OUTFILE) | awk '{print $$NF}'); \
			else \
				TEMPO="ERRO"; \
			fi; \
			echo "$$(basename $$f) | $${NUM_PONTOS} | $$t | $$TEMPO" >> $(RESULTS); \
		done; \
	done

# Gera plots (clusters, speedup, eficiência)
plots:
	@echo "Gerando gráficos de clusters e desempenho..."
	$(PYTHON) plot_kmeans.py

# Alvo completo: compila, executa e gera plots
all: $(EXEC) run plots

# Verifica se os arquivos de dados existem
check-data:
	@if [ ! -d $(DATA_DIR) ]; then \
		echo "ERRO: diretório '$(DATA_DIR)' não encontrado!"; \
		exit 1; \
	fi
	@for f in $(DATA_PATHS); do \
		if [ ! -f $$f ]; then \
			echo "AVISO: arquivo de dados '$$f' não encontrado."; \
		fi \
	done

# Remove arquivos gerados
clean:
	rm -f $(EXEC) $(RESULTS) $(OUTFILE)

# Remove tudo, incluindo cache Python e plots
distclean: clean
	rm -rf __pycache__ plots

.PHONY: run plots all clean distclean check-data
