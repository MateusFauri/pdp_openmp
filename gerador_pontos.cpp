#include <iostream>
#include <fstream>
#include <iomanip>
#include <random>
#include <filesystem>
#include <vector>

namespace fs = std::filesystem;

int main()
{
    std::vector<long long> quantidades_pontos = {
        1000,
        10000,
        100000,
        1000000,
        2000000,
    };

    double min_coord = 0.0;
    double max_coord = 100.0;
    int casas_decimais = 2;

    std::cout << "Iniciando a geracao dos arquivos TXT com pontos aleatorios (intervalo: ["
              << min_coord << ", " << max_coord << "])..." << std::endl;

    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<> dis(min_coord, max_coord);

    std::string dir = "arquivos_dados";
    if (!fs::exists(dir))
    {
        fs::create_directory(dir);
    }

    for (auto N : quantidades_pontos)
    {
        std::string nome_arquivo = "pontos_" + std::to_string(N) + ".txt";
        std::string path_arquivo = dir + "/" + nome_arquivo;

        std::ofstream arquivo(path_arquivo);
        if (!arquivo.is_open())
        {
            std::cerr << "Erro ao abrir o arquivo: " << path_arquivo << std::endl;
            continue;
        }

        for (long long i = 0; i < N; i++)
        {
            double x = dis(gen);
            double y = dis(gen);
            arquivo << std::fixed << std::setprecision(casas_decimais)
                    << x << " " << y << "\n";
        }

        arquivo.close();
        std::cout << "Arquivo '" << nome_arquivo << "' criado com sucesso, contendo "
                  << N << " pontos." << std::endl;
    }

    std::cout << "\nProcesso concluido." << std::endl;
    return 0;
}
