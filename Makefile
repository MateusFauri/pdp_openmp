CXX = g++
CXXFLAGS = -fopenmp 
SRC = k-means.cpp
EXEC = k-means_exec
GEN_SRC = gerador_pontos.cpp
GEN_EXEC = gerador_pontos_exec
PYTHON = python3
RESULTS = resultados.txt
OUTFILE = out.txt

$(EXEC): $(SRC)
	$(CXX) $(CXXFLAGS) $(SRC) -o $(EXEC)

$(GEN_EXEC): $(GEN_SRC)
	$(CXX) -std=c++17 -O2 $(GEN_SRC) -o $(GEN_EXEC)

generate: $(GEN_EXEC)
	./$(GEN_EXEC)

run: $(EXEC)
	./get_results.sh

plots:
	$(PYTHON) plot_kmeans.py

clean:
	rm -f $(EXEC) $(GEN_EXEC) $(RESULTS) $(OUTFILE)

.PHONY: run plots clean generate
