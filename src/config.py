# todo parametro do trabalho num lugar so, daí os outros scripts so importam esse config

# ASes russos alvo, cada um e uma rede grande da russia (confirmar o ASN na hora de puxar)
ases_alvo = {
    "Rostelecom": 12389,   # confirmado via RIPEstat/Kentik
    "TTK": 20485,          # transtelecom, confirmado via Kentik
    "MTS": 8359,           # confirmar
    "Beeline": 3216,       # vimpelcom, confirmar
    "MegaFon": 31133,      # confirmar
    "ER-Telecom": 9049,    # confirmar
}

# os dois upstreams ocidentais que sairam por causa da sancao, sao esses que a gente
# espera ver sumindo dos AS_PATH depois de inicio de marco
upstreams_ocidentais = {"Cogent": 174, "Lumen": 3356}

# possiveis substitutos que entraram no lugar (documentado pela Kentik), pra procurar no path
upstreams_substitutos = {"Vodafone": 1273, "TI_Sparkle": 6762, "Arelion": 1299}

# janela de analise, pega a base antes (jan-fev), o evento (marco) e uns meses depois
inicio = "2022-01-01"
fim = "2022-06-30"

# datas dos eventos pra marcar linha vertical nos graficos
evento_cogent = "2022-03-04"   # cogent encerra transito de redes russas
evento_lumen = "2022-03-08"    # lumen encerra transito de redes russas

# coletores do RIS/RouteViews
coletores = ["rrc00", "rrc12", "route-views2"]

# de quantos em quantos dias pega um snapshot de RIB
passo_dias = 7

# estudo de caso, a khersontelecom que trocou transito ucraniano por russo
kherson_as = 47598  # confirmar
