# le o rib_paths.csv (os AS_PATH historicos) e calcula as 3 metricas do trabalho:
#  1. fracao de rotas com cogent(174)/lumen(3356) como upstream DIRETO da rede russa, por
#     data (o efeito de "encerrar transito" aparece aqui, no salto logo antes do origin)
#  2. composicao de upstreams da rostelecom, antes vs depois do corte
#  3. tamanho medio do AS_PATH, por data
# cospe uma tabela pronta pra cada grafico

import pandas as pd

import config

COGENT = str(config.upstreams_ocidentais["Cogent"])   # "174"
LUMEN = str(config.upstreams_ocidentais["Lumen"])      # "3356"
OCID = {COGENT, LUMEN}
CORTE = "2022-03-10"   # corte foi 4-8/mar, entao ate 08/mar = antes, 15/mar+ = depois

# as redes russas que de fato usavam cogent/lumen como transito (as outras nunca usaram,
# entao nao mostram efeito, e a rostelecom era a cliente principal)
redes = {"Rostelecom": "12389", "TTK": "20485"}


# quebra "58057 174 12389" numa lista e tira repetido em sequencia (prepend)
def quebra_path(as_path):
    ases = str(as_path).split()
    limpo = []
    for a in ases:
        if not limpo or limpo[-1] != a:
            limpo.append(a)
    return limpo


# monta as colunas de origin (ultimo AS) e upstream (penultimo) uma vez so
def prepara(rib):
    rib = rib.copy()
    rib["ases"] = rib["as_path"].apply(quebra_path)
    rib["origin"] = rib["ases"].apply(lambda a: a[-1] if a else None)
    rib["upstream"] = rib["ases"].apply(lambda a: a[-2] if len(a) >= 2 else None)
    return rib


# metrica 1: por data, a fracao das rotas de cada rede russa que tem cogent ou lumen como
# upstream direto (o AS logo antes do origin)
def upstream_ocidental_no_tempo(rib):
    linhas = []
    for data, grupo in rib.groupby("data"):
        linha = {"data": data}
        for nome, asn in redes.items():
            sub = grupo[grupo["origin"] == asn]
            linha[nome] = sub["upstream"].isin(OCID).mean() if len(sub) else None
        linhas.append(linha)
    return pd.DataFrame(linhas).sort_values("data")


# metrica 2: composicao de upstreams da rostelecom, quantas vezes cada upstream aparece
# antes vs depois do corte
def composicao_upstreams(rib, asn="12389"):
    sub = rib[rib["origin"] == asn].copy()
    sub["janela"] = sub["data"].apply(lambda d: "antes" if d < CORTE else "depois")
    sub = sub.dropna(subset=["upstream"])
    return sub.groupby(["janela", "upstream"]).size().reset_index(name="contagem")


# metrica 3: tamanho medio do AS_PATH por data
def tamanho_medio(rib):
    rib = rib.copy()
    rib["tam"] = rib["ases"].apply(len)
    r = rib.groupby("data")["tam"].mean().reset_index()
    r.columns = ["data", "tamanho_medio"]
    return r.sort_values("data")


# metrica 4: concentracao do transito, a fracao das rotas nos 5 maiores upstreams de cada
# rede, por data. se cai, e porque o transito se espalhou por mais provedores
def concentracao_top5(rib):
    linhas = []
    for data, grupo in rib.groupby("data"):
        linha = {"data": data}
        for nome, asn in redes.items():
            sub = grupo[grupo["origin"] == asn]
            vc = sub["upstream"].value_counts(normalize=True)
            linha[nome] = vc.iloc[:5].sum() if len(vc) else None
        linhas.append(linha)
    return pd.DataFrame(linhas).sort_values("data")


def main():
    rib = pd.read_csv("data/processed/rib_paths.csv", dtype=str)
    # descarta datas com snapshot parcial (tipo a 05-15 que ficou pela metade no ctrl+c)
    cont = rib["data"].value_counts()
    rib = rib[rib["data"].isin(cont[cont > 50000].index)]

    rib = prepara(rib)
    upstream_ocidental_no_tempo(rib).to_csv("data/processed/metricas_upstream_ocidental.csv", index=False)
    composicao_upstreams(rib).to_csv("data/processed/metricas_composicao.csv", index=False)
    tamanho_medio(rib).to_csv("data/processed/metricas_tamanho.csv", index=False)
    concentracao_top5(rib).to_csv("data/processed/metricas_concentracao.csv", index=False)
    print("metricas salvas em data/processed/metricas_*.csv")


if __name__ == "__main__":
    main()
