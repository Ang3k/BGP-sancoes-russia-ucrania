# coleta o AS_PATH historico de 2022 dos dumps MRT do RIS. pra cada data-chave baixa o
# bview (tabela inteira), parseia com mrtparse e guarda so os prefixos originados pelos
# ASes russos alvo. baixa, parseia, salva e apaga o dump, e continua de onde parou

import csv
import os
import urllib.request

from mrtparse import Reader

import config

alvos = set(config.ases_alvo.values())

datas = ["2022-02-01", "2022-02-15", "2022-03-01", "2022-03-08", "2022-03-15", "2022-04-01", "2022-04-15", "2022-05-01"]


def baixa_bview(data):
    ano, mes, dia = data.split("-")
    arq = f"bview_{data}.gz"
    if os.path.exists(arq):
        return arq   # reaproveita se ja baixou
    for hora in ["0000", "0800", "1600"]:
        url = f"https://data.ris.ripe.net/rrc00/{ano}.{mes}/bview.{ano}{mes}{dia}.{hora}.gz"
        try:
            print("  baixando", url)
            urllib.request.urlretrieve(url, arq)
            return arq
        except Exception as erro:
            print("   nao rolou", hora, erro.__class__.__name__)
    return None


# tira a sequencia de ASes do AS_PATH. o 'type' vem como dict {2: 'AS_PATH'}, entao
# AS_PATH e quando o 2 e chave, e cada segmento tem a lista de ASes em seg['value']
def path_do_rib(rib):
    for attr in rib.get("path_attributes", []):
        tipo = attr.get("type") or {}
        if 2 in tipo:   # 2 = AS_PATH
            seq = []
            for seg in attr.get("value", []):
                seq += [str(a) for a in seg.get("value", [])]
            return seq
    return []


def datas_ja_feitas(caminho):
    if not os.path.exists(caminho):
        return set()
    feitas = set()
    with open(caminho) as entrada:
        leitor = csv.reader(entrada)
        next(leitor, None)
        for linha in leitor:
            if linha:
                feitas.add(linha[0])
    return feitas


def coleta_data(data, escritor):
    arq = baixa_bview(data)
    if arq is None:
        print(data, "sem dump, pulei")
        return
    print("  parseando", data, "(uns minutos)...")
    lidos = 0
    achados = 0
    for m in Reader(arq):
        d = m.data
        lidos += 1
        if lidos % 200000 == 0:
            print("   ...", lidos, "lidos,", achados, "rotas russas")
        ribs = d.get("rib_entries")
        if not ribs:
            continue
        mask = d.get("prefix_length")
        if mask is None:
            mask = d.get("length")
        prefixo = str(d.get("prefix")) + "/" + str(mask)
        for rib in ribs:
            seq = path_do_rib(rib)
            if not seq:
                continue
            try:
                origin = int(seq[-1])
            except ValueError:
                continue
            if origin in alvos:
                escritor.writerow([data, prefixo, " ".join(seq), rib.get("peer_index")])
                achados += 1
    os.remove(arq)
    print(data, "ok,", achados, "rotas russas")


def main():
    caminho = "data/processed/rib_paths.csv"
    feitas = datas_ja_feitas(caminho)
    arquivo_novo = (not os.path.exists(caminho)) or os.path.getsize(caminho) == 0

    with open(caminho, "a", newline="") as saida:
        escritor = csv.writer(saida)
        if arquivo_novo:
            escritor.writerow(["data", "prefixo", "as_path", "peer"])
        for data in datas:
            if data in feitas:
                print(data, "ja tinha, pulei")
                continue
            coleta_data(data, escritor)
            saida.flush()

    print("acabou")


if __name__ == "__main__":
    main()
