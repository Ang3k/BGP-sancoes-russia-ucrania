# puxa, pra cada prefixo alvo, o estado da tabela (RIB) num dia pela RIPEstat bgp-state,
# que devolve os AS_PATH que cada peer do RIS via naquele momento, pega um snapshot a
# cada passo_dias ao longo da janela
# so precisa de requests. tres coisas importantes aqui: aguenta timeout da api tentando
# de novo, grava o csv dia a dia (se travar nao perde o que ja veio) e continua de onde
# parou se rodar de novo

import csv
import os
import time
from datetime import datetime, timedelta

import requests

import config


# faz o request tentando algumas vezes, se a api travar ou der timeout espera um pouco e
# tenta de novo, e se nao rolar depois das tentativas devolve None pra gente pular em vez
# de morrer
def pega_json(url, parametros, tentativas=3):
    for i in range(tentativas):
        try:
            resposta = requests.get(url, params=parametros, timeout=45)
            return resposta.json()
        except Exception as erro:
            print("   request travou, tentando de novo", i + 1, erro.__class__.__name__)
            time.sleep(3)
    return None


# os prefixos que um AS anuncia, so uns poucos por AS pra coleta nao demorar uma vida
def prefixos_do_as(numero_as, limite=6):
    dados = pega_json("https://stat.ripe.net/data/announced-prefixes/data.json",
                      {"resource": "AS" + str(numero_as)})
    if dados is None:
        return []
    prefixos = [item["prefix"] for item in dados["data"]["prefixes"]]
    prefixos_v4 = [p for p in prefixos if ":" not in p]   # so v4 por enquanto
    return prefixos_v4[:limite]


# o estado da tabela pra um prefixo num dia, devolve os AS_PATH vistos pelos peers do RIS
def bgp_state(prefixo, data):
    dados = pega_json("https://stat.ripe.net/data/bgp-state/data.json",
                      {"resource": prefixo, "query_time": data + "T00:00:00"})
    if dados is None:
        return []   # pulou esse prefixo nesse dia, segue a vida
    # as vezes a api responde sem a chave bgp_state (prefixo sem estado naquele instante),
    # entao pega com get e se nao tiver vira lista vazia, sem quebrar
    estado = dados.get("data", {}).get("bgp_state", [])
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


# as datas que ja estao no csv, pra continuar de onde parou. como a gente so grava depois
# de terminar o dia inteiro, toda data que ta no arquivo ta completa
def datas_ja_feitas(caminho):
    if not os.path.exists(caminho):
        return set()
    feitas = set()
    with open(caminho) as entrada:
        leitor = csv.reader(entrada)
        next(leitor, None)   # pula o cabecalho
        for linha in leitor:
            if linha:
                feitas.add(linha[0])
    return feitas


def main():
    caminho = "data/processed/rib_paths.csv"

    prefixos = []
    for nome, numero in config.ases_alvo.items():
        achados = prefixos_do_as(numero)
        print(numero, nome, len(achados))
        prefixos = prefixos + achados

    feitas = datas_ja_feitas(caminho)
    arquivo_novo = (not os.path.exists(caminho)) or os.path.getsize(caminho) == 0

    with open(caminho, "a", newline="") as saida:
        escritor = csv.writer(saida)
        if arquivo_novo:
            escritor.writerow(["data", "prefixo", "as_path", "peer"])
        for data in dias_da_janela():
            if data in feitas:
                print(data, "ja tinha, pulei")
                continue
            for prefixo in prefixos:
                escritor.writerows(bgp_state(prefixo, data))
            saida.flush()   # grava o dia inteiro de uma vez, daí se travar nao perde
            print(data, "ok")

    print("acabou")


if __name__ == "__main__":
    main()
