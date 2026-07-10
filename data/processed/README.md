# Proveniência dos dados

De onde veio cada arquivo de `data/processed/`, pra qualquer um refazer a coleta e bater os números.

## rib_paths.csv
- **O que é:** os AS_PATH de todos os prefixos originados pelos 6 ASes russos alvo, em 8 datas de 2022.
- **Fonte:** RIPE RIS, coletor **rrc00**, arquivos MRT (RIB dumps / bview) baixados de https://data.ris.ripe.net/rrc00/
- **Datas:** 2022-02-01, 02-15, 03-01, 03-08, 03-15, 04-01, 04-15, 05-01 (bview das 00:00 UTC de cada dia).
- **Gerado por:** `src/coleta_rib_hist.py` (baixa o bview, parseia com mrtparse, filtra origin nos ASes alvo).
- **Colunas:** `data, prefixo, as_path, peer`.
- **Obs:** por que MRT e não a API ao vivo — o RIPEstat bgp-state/bgp-updates/bgplay não retorna mais 2022 (retenção curta); os arquivos MRT do RIS guardam o histórico de forma permanente.

## metricas_upstream_ocidental.csv, metricas_composicao.csv, metricas_tamanho.csv
- **O que é:** as 3 tabelas de métrica já prontas pros gráficos.
- **Fonte:** derivadas do rib_paths.csv.
- **Gerado por:** `src/metricas.py`.

## caso_kherson.csv
- **O que é:** o histórico de origin do AS47598 (Khersontelecom) ao longo de 2022.
- **Fonte:** RIPEstat routing-history (HTTP/JSON).
- **Gerado por:** `src/caso_kherson.py`.

## Ressalva de visibilidade
Os números refletem o que os peers do rrc00 enxergam, não a Internet inteira. O que é mais robusto é a variação antes/depois dentro do mesmo coletor, não as frações absolutas.
