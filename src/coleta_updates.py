# conta os withdrawals por dia de cada prefixo alvo pela RIPEstat bgp-updates, que lista
# os anuncios e withdrawals no intervalo, o withdrawal e o type "W"
# so precisa de requests

import csv
from collections import defaultdict

import requests

import config
from coleta_rib import prefixos_do_as


# os updates de um prefixo na janela, se a api reclamar do intervalo grande e so quebrar
# em pedacos menores (mes a mes) e juntar
def updates_do_prefixo(prefixo):
    url = "https://stat.ripe.net/data/bgp-updates/data.json"
    parametros = {"resource": prefixo, "starttime": config.inicio, "endtime": config.fim}
    resposta = requests.get(url, params=parametros, timeout=120)
    return resposta.json()["data"]["updates"]


def main():
    prefixos = []
    for nome, numero in config.ases_alvo.items():
        prefixos = prefixos + prefixos_do_as(numero)

    contagem = defaultdict(int)   # (data, prefixo) -> qtd de W
    for prefixo in prefixos:
        for upd in updates_do_prefixo(prefixo):
            if upd.get("type") == "W":
                data = upd["timestamp"][:10]   # so a parte YYYY-MM-DD
                contagem[(data, prefixo)] += 1
        print(prefixo, "ok")

    with open("data/processed/withdrawals.csv", "w", newline="") as saida:
        escritor = csv.writer(saida)
        escritor.writerow(["data", "prefixo", "quantidade"])
        for (data, prefixo) in sorted(contagem.keys()):
            escritor.writerow([data, prefixo, contagem[(data, prefixo)]])


if __name__ == "__main__":
    main()
