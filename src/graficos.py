# gera os 3 graficos do relatorio a partir das tabelas de metrica, formatacao limpa:
#  G1 = fracao de rotas com cogent/lumen como upstream direto, por rede russa, no tempo
#  G2 = composicao dos principais upstreams da rostelecom, antes vs depois
#  G3 = tamanho medio do AS_PATH no tempo
# saem em figuras/ como png (pra ver) e pdf (vetorial, pro relatorio)

import pandas as pd
import matplotlib.pyplot as plt

import config

plt.rcParams.update({
    "figure.figsize": (8, 4.5),
    "figure.dpi": 150,
    "axes.grid": True,
    "grid.alpha": 0.25,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "font.size": 11,
})

nomes_as = {
    "174": "Cogent", "3356": "Lumen", "1299": "Arelion", "6762": "TI Sparkle",
    "1273": "Vodafone", "6939": "Hurricane", "9002": "RETN", "5511": "Orange",
    "3491": "PCCW", "3257": "GTT", "2914": "NTT",
}


def nome(asn):
    return nomes_as.get(str(asn), "AS" + str(asn))


# faixa do evento (4 a 8 de marco, quando cogent e lumen sairam)
def marca_corte(ax):
    ini = pd.to_datetime(config.evento_cogent)
    fim = pd.to_datetime(config.evento_lumen)
    ax.axvspan(ini, fim, color="#d1495b", alpha=0.13)
    meio = ini + (fim - ini) / 2
    ax.annotate("saída\nCogent/Lumen", xy=(meio, 0.97), xycoords=("data", "axes fraction"),
                ha="center", va="top", fontsize=7.5, color="#a03040")


def salva(fig, base):
    fig.tight_layout()
    fig.savefig(f"figuras/{base}.png", bbox_inches="tight")
    fig.savefig(f"figuras/{base}.pdf", bbox_inches="tight")
    plt.close(fig)


def grafico_upstream_ocidental():
    tab = pd.read_csv("data/processed/metricas_upstream_ocidental.csv")
    tab["data"] = pd.to_datetime(tab["data"])
    fig, ax = plt.subplots()
    ax.plot(tab["data"], tab["Rostelecom"], marker="o", color="#30638e", linewidth=2, label="Rostelecom (AS12389)")
    ax.plot(tab["data"], tab["TTK"], marker="s", color="#edae49", linewidth=2, label="TTK (AS20485)")
    marca_corte(ax)
    ax.set_ylabel("fração das rotas com Cogent/Lumen\ncomo upstream direto")
    ax.set_xlabel("data")
    ax.set_ylim(0.05, 0.4)
    ax.set_title("Cogent/Lumen como provedor de trânsito direto de redes russas")
    ax.legend(frameon=False, fontsize=9)
    salva(fig, "g1")


def grafico_composicao():
    cont = pd.read_csv("data/processed/metricas_composicao.csv", dtype={"upstream": str})
    total = cont.groupby("janela")["contagem"].transform("sum")
    cont["fracao"] = cont["contagem"] / total
    top = cont.groupby("upstream")["fracao"].sum().sort_values(ascending=False).head(7).index
    cont = cont[cont["upstream"].isin(top)]
    pivo = cont.pivot_table(index="upstream", columns="janela", values="fracao", fill_value=0)
    for col in ["antes", "depois"]:
        if col not in pivo.columns:
            pivo[col] = 0
    pivo = pivo.loc[pivo[["antes", "depois"]].max(axis=1).sort_values().index]

    fig, ax = plt.subplots()
    y = range(len(pivo))
    alt = 0.38
    ax.barh([i + alt / 2 for i in y], pivo["antes"], height=alt, label="antes (até o corte)", color="#30638e")
    ax.barh([i - alt / 2 for i in y], pivo["depois"], height=alt, label="depois (15 mar–1 mai)", color="#d1495b")
    ax.set_yticks(list(y))
    ax.set_yticklabels([f"{nome(a)} ({a})" for a in pivo.index])
    ax.set_xlabel("fração das rotas da Rostelecom onde é o upstream direto")
    ax.set_title("Upstreams diretos da Rostelecom: antes vs depois do corte")
    ax.legend(frameon=False, fontsize=9, loc="lower right")
    salva(fig, "g2")


def grafico_tamanho():
    tab = pd.read_csv("data/processed/metricas_tamanho.csv")
    tab["data"] = pd.to_datetime(tab["data"])
    fig, ax = plt.subplots()
    ax.plot(tab["data"], tab["tamanho_medio"], marker="o", color="#30638e", linewidth=2)
    marca_corte(ax)
    ax.set_ylabel("tamanho médio do AS_PATH")
    ax.set_xlabel("data")
    # eixo aproximado nos pontos (que ficam ~3,4) pra dar pra ver a variacao, que e pequena
    ax.set_ylim(3.40, 3.50)
    ax.set_title("Tamanho médio do AS_PATH dos prefixos russos alvo")
    salva(fig, "g3")


def grafico_concentracao():
    tab = pd.read_csv("data/processed/metricas_concentracao.csv")
    tab["data"] = pd.to_datetime(tab["data"])
    fig, ax = plt.subplots()
    ax.plot(tab["data"], tab["Rostelecom"], marker="o", color="#30638e", linewidth=2, label="Rostelecom (AS12389)")
    ax.plot(tab["data"], tab["TTK"], marker="s", color="#edae49", linewidth=2, label="TTK (AS20485)")
    marca_corte(ax)
    ax.set_ylabel("fração das rotas nos 5 maiores upstreams")
    ax.set_xlabel("data")
    ax.set_ylim(0, 1)
    ax.set_title("Concentração do trânsito das redes russas (top-5 upstreams)")
    ax.legend(frameon=False, fontsize=9)
    salva(fig, "g4")


def main():
    grafico_upstream_ocidental()
    grafico_composicao()
    grafico_tamanho()
    grafico_concentracao()
    print("figuras salvas em figuras/ (g1, g2, g3 em png e pdf)")


if __name__ == "__main__":
    main()
