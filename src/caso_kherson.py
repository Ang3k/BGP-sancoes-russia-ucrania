# estudo de caso da khersontelecom (AS47598): pega o historico de roteamento dela pela
# RIPEstat routing-history (uma das poucas fontes HTTP que ainda tem 2022) e monta a
# linha do tempo do origin ao longo da janela, gerando a figura g4. so precisa de
# requests, pandas e matplotlib

import csv

import requests
import pandas as pd
import matplotlib.pyplot as plt

import config


def historico(numero_as):
    url = "https://stat.ripe.net/data/routing-history/data.json"
    parametros = {"resource": "AS" + str(numero_as),
                  "starttime": config.inicio, "endtime": config.fim}
    return requests.get(url, params=parametros, timeout=120).json()["data"]


def main():
    dados = historico(config.kherson_as)

    # a routing-history vem por origin, cada um com os prefixos e as janelas de tempo em
    # que aquele origin anunciava, dai lineariza isso numa lista simples
    linhas = []
    for entrada in dados.get("by_origin", []):
        origin = entrada.get("origin")
        for prefixo_info in entrada.get("prefixes", []):
            prefixo = prefixo_info.get("prefix")
            for janela in prefixo_info.get("timelines", []):
                linhas.append([janela.get("starttime"), janela.get("endtime"), prefixo, origin])

    linhas.sort()
    with open("data/processed/caso_kherson.csv", "w", newline="") as saida:
        escritor = csv.writer(saida)
        escritor.writerow(["inicio", "fim", "prefixo", "origin"])
        escritor.writerows(linhas)

    # figura g4: cada origin distinto vira uma faixa no eixo y, dai da pra ver o momento
    # que o prefixo troca de origin ucraniano pra russo
    origins = sorted({linha[3] for linha in linhas})
    posicao = {origin: i for i, origin in enumerate(origins)}
    plt.figure(figsize=(8, 3.5))
    for inicio, fim, prefixo, origin in linhas:
        plt.plot([pd.to_datetime(inicio), pd.to_datetime(fim)],
                 [posicao[origin], posicao[origin]], linewidth=5)
    plt.yticks(range(len(origins)), origins)
    plt.xlabel("data")
    plt.ylabel("origin AS")
    plt.title("Khersontelecom (AS47598): origin do prefixo ao longo de 2022")
    plt.tight_layout()
    plt.savefig("figuras/caso_kherson.png", dpi=150)
    plt.savefig("figuras/caso_kherson.pdf")
    plt.close()
    print("salvei data/processed/caso_kherson.csv e figuras/caso_kherson")


if __name__ == "__main__":
    main()
