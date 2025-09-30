import random
import os

quantidades_pontos = [1000, 10000, 100000, 1000000]

min_coord = 0.0
max_coord = 100.0

casas_decimais = 2

print(f"Iniciando a geração dos arquivos TXT com pontos aleatórios (intervalo: [{min_coord}, {max_coord}])...")

for N in quantidades_pontos:
    dir = "arquivos_dados"
    if not os.path.exists(dir):
        os.makedirs(dir)

    nome_arquivo = f"pontos_{N}.txt"
    path_arquivo = os.path.join(dir, nome_arquivo)
    
    with open(path_arquivo, 'w') as arquivo:
        for _ in range(N):
            x = random.uniform(min_coord, max_coord)
            y = random.uniform(min_coord, max_coord)
            
            formato = f"%.{casas_decimais}f %." + f"{casas_decimais}f\n"
            linha = formato % (x, y)
            
            arquivo.write(linha)
    
    print(f"Arquivo '{nome_arquivo}' criado com sucesso, contendo {N:,} pontos.")

print("\nProcesso concluído.")