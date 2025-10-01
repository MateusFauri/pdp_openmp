CXX = g++
CXXFLAGS = -fopenmp 
SRC = k-means.cpp
EXEC = k-means_exec
PYTHON = python3
RESULTS = resultados.txt
OUTFILE = out.txt


$(EXEC): $(SRC)
	$(CXX) $(CXXFLAGS) $(SRC) -o $(EXEC)

run: $(EXEC)
	./get_results.sh

plots:
	$(PYTHON) plot_kmeans.py

clean:
	rm -f $(EXEC) $(RESULTS) $(OUTFILE)

.PHONY: run plots  clean 
