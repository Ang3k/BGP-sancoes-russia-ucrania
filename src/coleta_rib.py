# pra cada AS russo alvo pega os prefixos que ele anuncia, daí ao longo da janela vai
# pegando um snapshot de RIB a cada passo_dias e guardando os AS_PATH desses prefixos,
# isso vira a base das metricas 1, 2 e 3

import csv
from datetime import datetime, timedelta

import requests
import pybgpstream

import config


# pega os prefixos que um AS anuncia pela RIPEstat, mais facil doque varrer a tabela
# inteira so pra descobrir os prefixos
def prefixos_do_as(numero_as, limite=15):
    url = "https://stat.ripe.net/data/announced-prefixes/data.json"
    resposta = requests.get(url, params={"resource": "AS" + str(numero_as)}, timeout=60)
    dados = resposta.json()
    prefixos = [item["prefix"] for item in dados["data"]["prefixes"]]
    prefixos_v4 = [p for p in prefixos if ":" not in p]   # so v4 por enquanto
    return prefixos_v4[:limite]


# pega a RIB de um dia e devolve as linhas dos prefixos que interessam
def coleta_dia(data, prefixos):
    linhas = []
    prefixos_set = set(prefixos)
    stream = pybgpstream.BGPStream(
        from_time=data + " 00:00:00", until_time=data + " 00:30:00",
        collectors=config.coletores, record_type="ribs",
    )
    for elem in stream:
        prefixo = elem.fields.get("prefix")
        if prefixo in prefixos_set:
            linhas.append([data, prefixo, elem.fields.get("as-path"), elem.collector])
    return linhas


# as datas da janela, de passo_dias em passo_dias
def dias_da_janela():
    atual = datetime.strptime(config.inicio, "%Y-%m-%d")
    final = datetime.strptime(config.fim, "%Y-%m-%d")
    datas = []
    while atual <= final:
        datas.append(atual.strftime("%Y-%m-%d"))
        atual = atual + timedelta(days=config.passo_dias)
    return datas


def main():
    prefixos = []
    for nome, numero in config.ases_alvo.items():
        achados = prefixos_do_as(numero)
        print(numero, nome, len(achados))
        prefixos = prefixos + achados

    with open("data/processed/rib_paths.csv", "w", newline="") as saida:
        escritor = csv.writer(saida)
        escritor.writerow(["data", "prefixo", "as_path", "coletor"])
        for data in dias_da_janela():
            linhas = coleta_dia(data, prefixos)
            escritor.writerows(linhas)
            print(data, len(linhas))


if __name__ == "__main__":
    main()
