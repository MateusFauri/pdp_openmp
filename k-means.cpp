#include <iostream>
#include <vector>
#include <fstream>
#include <algorithm>
#include <cmath>
#include <memory>
#include <random>
#include <limits>
#include <string>
#include <sstream>
#include <omp.h>
#include <cstdlib> 

struct point {
    double x, y;
    int cluster = -1;
};

int main(int argc, char* argv[])
{
    if (argc != 4) {
        std::cerr << "Uso: " << argv[0] << " <numero_de_iteracoes> <numero_de_clusters> <nome_do_arquivo>" << std::endl;
        return 1;
    }

    unsigned int t, k; // t - número de iterações do algoritmo, k - quantidade de clusters
    std::string filename;

    try {
        t = std::stoul(argv[1]);
        k = std::stoul(argv[2]);
        filename = argv[3];
    } catch (const std::exception& e) {
        std::cerr << "Erro na conversão dos argumentos: " << e.what() << std::endl;
        std::cerr << "Certifique-se de que <numero_de_iteracoes> e <numero_de_clusters> são números inteiros positivos." << std::endl;
        return 1;
    }

    std::vector<point> init;
    std::ifstream file(filename);

    if (!file.is_open()) {
        std::cerr << "Erro: Não foi possível abrir o arquivo " << filename << std::endl;
        return 1;
    }

    std::string line;
    while (std::getline(file, line)) {
        std::stringstream ss(line);
        point tmp;
        if (ss >> tmp.x >> tmp.y) {
            init.push_back(tmp);
        }
    }
    file.close();

    if (init.empty()) {
        std::cerr << "Erro: Arquivo de entrada vazio ou inválido." << std::endl;
        return 1;
    }
    
    double max_x = std::numeric_limits<double>::lowest();
    double max_y = std::numeric_limits<double>::lowest();
    double min_x = std::numeric_limits<double>::max();
    double min_y = std::numeric_limits<double>::max();

    for (const auto& p : init) {
        if (p.x > max_x) max_x = p.x;
        if (p.y > max_y) max_y = p.y;
        if (p.x < min_x) min_x = p.x;
        if (p.y < min_y) min_y = p.y;
    }

    std::vector<point> centers(k);
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<> distrib_x(min_x, max_x);
    std::uniform_real_distribution<> distrib_y(min_y, max_y);

    for (unsigned int i = 0; i < k; i++) {
        centers[i].x = distrib_x(gen);
        centers[i].y = distrib_y(gen);
    }

    double t_inicial = omp_get_wtime();

    for (unsigned int i = 0; i < t; i++) { // USA VALORES DA EXECUÇÃO ANTERIOR ENTÃO NÃO É BOM PARALELIZAR
        #pragma omp parallel for //private (min_dist, closest_cluster, p, a, b, dist, sum_x, sum_y, count, f) -- não precisa pois são declaradas dentro do loop (tratadas de cara como private)
        for (unsigned int j = 0; j < init.size(); j++) {
            double min_dist = -1.0;
            int closest_cluster = -1;

            for (unsigned int p = 0; p < k; p++) {
                double a = std::abs(init[j].y - centers[p].y);
                double b = std::abs(init[j].x - centers[p].x);
                double dist = std::sqrt(std::pow(a, 2) + std::pow(b, 2));

                if (closest_cluster == -1 || dist < min_dist) {
                    min_dist = dist;
                    closest_cluster = p;
                }
            }
            init[j].cluster = closest_cluster;
        }

        std::vector<double> sum_x(k, 0.0);
        std::vector<double> sum_y(k, 0.0);
        std::vector<int> count(k, 0);

        // Verificar se vale a pena deixar esse loop paralelo, fazer os testes de desempenho
        #pragma omp parallel for
        for (int f = 0; f < init.size(); f++) {
            int c = init[f].cluster;
            #pragma omp atomic
            sum_x[c] += init[f].x;
            #pragma omp atomic
            sum_y[c] += init[f].y;
            #pragma omp atomic
            count[c]++;
        }
        
        for (unsigned int f = 0; f < k; f++) {
            if (count[f] > 0) {
                centers[f].x = sum_x[f] / count[f];
                centers[f].y = sum_y[f] / count[f];
            }
        }
    }
    double t_final = omp_get_wtime();

    std::ofstream ofile("out.txt");
    if (!ofile.is_open()) {
        std::cerr << "Error: Unable to create output file." << std::endl;
        return 1;
    }
    ofile << "Tempo gasto no loop: " << t_final - t_inicial << "\n";

    for (unsigned int i = 0; i < init.size(); i++) {
        ofile << init[i].x << ", " << init[i].y << " -> " << init[i].cluster << "\n";
    }
    ofile.close();

    return 0;
}