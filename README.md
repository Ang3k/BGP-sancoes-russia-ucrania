# Sanções e roteamento: a saída de provedores de trânsito ocidentais de redes russas no BGP após fev/2022

Trabalho final da disciplina de Redes (BGP, Internet e geopolítica). A ideia aqui é pegar uma dimensão técnica observável no BGP e cruzar com uma questão geopolítica atual, pra ver se a coisa deixa rastro nos dados públicos de roteamento.

**Tema:** analisar a dimensão **A2 — sanções econômicas e tecnológicas** em relação à questão **B1 — guerra Rússia–Ucrânia**, usando dados públicos de BGP.

Em concreto: depois das sanções, a Cogent (AS174) saiu do trânsito de redes russas em 4/mar/2022 e a Lumen (AS3356) em 8/mar/2022, e a pergunta é se isso aparece no plano de controle, ou seja se esses dois ASes somem dos AS_PATHs pros prefixos russos e são substituídos (mesmo que só em parte) por outros upstreams.

## O que tem aqui

- `src/` = os scripts, um pra cada parte (config, coleta de RIB, coleta de updates, métricas, gráficos, estudo de caso)
- `data/processed/` = os CSVs que saem das coletas (versionados)
- `figuras/` = os gráficos que vão pro relatório

## Como rodar

Precisa de Python 3 e das libs do `requirements.txt`. A coleta usa o `pybgpstream`, que depende do `libbgpstream` instalado no sistema **antes** do pip:

```
# no ubuntu/debian, instalar o libbgpstream primeiro (ver docs do CAIDA/bgpstream)
pip install -r requirements.txt
```

Daí roda na ordem:

```
python src/coleta_rib.py        # puxa os RIB e tira os AS_PATH dos prefixos alvo
python src/coleta_updates.py    # puxa os updates e conta os withdrawals por dia
python src/metricas.py          # calcula as métricas a partir dos CSVs
python src/graficos.py          # gera as figuras do relatório
python src/caso_kherson.py      # estudo de caso da khersontelecom
```

Se o `pybgpstream` der trabalho pra instalar, dá pra fazer quase tudo pela RIPEstat Data API só com `requests` (tá comentado nos scripts onde encaixa).

## Janela de análise

1/jan/2022 a 30/jun/2022, pega a linha de base antes (jan–fev), o evento (início de março) e alguns meses depois (abr–jun).

## Entregáveis

1. relatório PDF em formato SBC + link do Overleaf
2. este repositório com código e dados

## Achados

(preencher com os números reais depois da coleta)
