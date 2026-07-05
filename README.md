# Sanções e roteamento: Cogent/Lumen e as redes russas no BGP (2022)

Trabalho final de Redes. Analisa a dimensão A2 (sanções) em relação à questão B1 (guerra Rússia–Ucrânia), usando dados públicos de BGP: depois das sanções, a Cogent (AS174) e a Lumen (AS3356) saíram do trânsito de redes russas em março/2022, e a ideia é ver se isso deixa rastro no roteamento. Deixa — a fração de rotas da Rostelecom com Cogent/Lumen como upstream direto cai de ~0,35 pra 0,24 logo após o corte e recupera parcialmente, com Vodafone e Orange ocupando o lugar.

Os dados vêm dos RIB dumps do RIPE RIS (coletor rrc00, 8 datas de fev a mai/2022), parseados com mrtparse. O relatório em formato SBC está em `relatorio/`.

Pra rodar:

```
pip install -r requirements.txt
python src/coleta_rib_hist.py   # baixa os RIB dumps e monta o rib_paths.csv
python src/metricas.py          # calcula as métricas
python src/graficos.py          # gera os gráficos
python src/caso_kherson.py      # estudo de caso da Khersontelecom
```

Relatório (Overleaf): https://www.overleaf.com/7292265121tgchywxctpmc#cf8540
