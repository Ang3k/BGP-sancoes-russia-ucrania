# puxa, pra cada prefixo alvo, o estado da tabela (RIB) num instante pela RIPEstat
# bgp-state, que devolve os AS_PATH que cada peer do RIS via naquele momento, daí pega
# um snapshot a cada passo_dias ao longo da janela
# so precisa de requests, bate direto na api, sem pybgpstream

import csv
import time
from datetime import datetime, timedelta

import requests

import config


# os prefixos que um AS anuncia, pela RIPEstat
def prefixos_do_as(numero_as, limite=15):
    url = "https://stat.ripe.net/data/announced-prefixes/data.json"
    resposta = requests.get(url, params={"resource": "AS" + str(numero_as)}, timeout=60)
    dados = resposta.json()
    prefixos = [item["prefix"] for item in dados["data"]["prefixes"]]
    prefixos_v4 = [p for p in prefixos if ":" not in p]   # so v4 por enquanto
    return prefixos_v4[:limite]


# o estado da tabela pra um prefixo num dia, devolve os AS_PATH vistos pelos peers do RIS
def bgp_state(prefixo, data):
    url = "https://stat.ripe.net/data/bgp-state/data.json"
    parametros = {"resource": prefixo, "timestamp": data + "T00:00:00"}
    resposta = requests.get(url, params=parametros, timeout=120)
    estado = resposta.json()["data"]["bgp_state"]
    linhas = []
    for rota in estado:
        caminho = " ".join(str(asn) for asn in rota["path"])
        linhas.append([data, prefixo, caminho, rota.get("source_id", "")])
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
        escritor.writerow(["data", "prefixo", "as_path", "peer"])
        for data in dias_da_janela():
            for prefixo in prefixos:
                escritor.writerows(bgp_state(prefixo, data))
                time.sleep(0.2)   # um respiro pra nao martelar a api
            print(data, "ok")


if __name__ == "__main__":
    main()
