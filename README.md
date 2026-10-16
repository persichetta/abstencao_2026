# longe da urna

mapa das regiões onde muita gente mora a mais de 1 hora a pé (5 km ou mais, em linha reta) da seção eleitoral mais próxima, com filtros de voto no lula e abstenção no 1º turno de 2026.

- **tela inicial**: busca por cidade, filtros "regiões longe da urna", "lula forte (60%+)" e "muita abstenção (22%+)", mapa dos municípios pela parcela de áreas habitadas longe da seção, e a lista de onde mais gente mora longe da urna;
- **município**: diz se é região longe ou perto das seções, com voto no lula, abstenção e os locais de votação que atendem regiões longe;
- **estado**: pontos vermelhos marcam as áreas habitadas a 5 km ou mais da seção; locais de votação com anel atendem regiões longe;
- **local de votação**: distância média de quem mora na região, voto no lula, abstenção e seções;
- **mais opções**: colorir o mapa por voto no lula ou abstenção.

uma área habitada é um setor censitário do censo 2022; um município é região longe quando 20% ou mais das suas áreas habitadas ficam a 5 km ou mais da seção mais próxima.

pela lei 6.091/1974, no dia da eleição o transporte de eleitores por terceiros é proibido (o eleitor e a família podem usar o próprio veículo); a justiça eleitoral oferece transporte gratuito nas zonas rurais.

## como publicar

é um site estático (`index.html` + `data/*.json`), sem build.

1. suba o conteúdo desta pasta na raiz de um repositório no github;
2. em **settings → pages**, escolha *deploy from a branch*, branch `main`, pasta `/ (root)`;
3. o site fica em `https://<usuario>.github.io/<repositorio>/` em um ou dois minutos.

pra testar localmente: `python3 -m http.server` dentro da pasta e abrir `http://localhost:8000` (abrir o html direto do disco não funciona, porque o navegador bloqueia o carregamento dos json).

## dados

| camada | fonte |
|---|---|
| abstenção por município e zona | tse, `detalhe_votacao_munzona_2026` (cargo presidente, 1º turno, sem exterior) |
| votos no lula por município e zona | tse, `votacao_candidato_munzona_2026` (arquivo `_BR`, presidente, 1º turno, candidato 13), sobre os votos válidos da zona |
| votos no lula por seção | tse, `votacao_secao_2026` (arquivo `_BR`, presidente, 1º turno) |
| sede dos municípios | [kelvins/municipios-brasileiros](https://github.com/kelvins/municipios-brasileiros) |
| abstenção por seção | tse, `detalhe_votacao_secao_2026` (arquivo `_BR`, cargo presidente) |
| coordenadas dos locais | tse, `eleitorado_local_votacao_2026` (1º turno) |
| malha municipal | ibge, via [geodata-br](https://github.com/tbrugz/geodata-br) |
| códigos tse → ibge | [betafcc/Municipios-Brasileiros-TSE](https://github.com/betafcc/Municipios-Brasileiros-TSE) |
| tipo de área | ibge, malha de setores censitários do censo 2022 (`CD_SIT`, `CD_TIPO`, `NM_BAIRRO`) |

abstenção = abstenções ÷ eleitores aptos. votos no lula = votos nominais do lula ÷ votos válidos para presidente.

### arquivos em `data/`

um json por uf com a lista de locais de votação. cada item é:

`[lat, lon, nome_local, municipio, zona, bairro, [[secao, aptos, abstencoes, votos_lula, votos_validos], ...], tipo_area, km_ate_sede, distancia_antiga, [setores_atendidos, km_medio, km_maximo]]`

`far/*.json`: setores censitários a 2 km ou mais da seção mais próxima, `[lat, lon, km]`.

`distancia`: 0 baixa · 1 média · 2 alta. alta = setor rural disperso, indígena ou quilombola, ou fora da área urbana adensada a 25 km+ da sede; média = povoado, núcleo urbano, urbana de baixa densidade, ou 8–25 km da sede; baixa = o restante.

códigos de `tipo_area`: 0 centro · 1 favela e comunidade urbana · 2 urbana alta densidade · 3 urbana baixa densidade · 4 núcleo urbano · 5 rural aglomerado · 6 rural área dispersa · 7 indígena ou quilombola · 8 outro · `null` sem setor.

## limitações

- a estimativa de eleitores do lula entre os ausentes supõe que quem faltou votaria como quem compareceu na mesma seção;
- a distância da região até a seção é em linha reta, do ponto interno de cada setor censitário até o local de votação mais próximo do mesmo município; pela estrada ou pelo rio costuma ser mais, e o eleitor nem sempre vota no local mais próximo de casa;
- 2.648 seções (0,5%) não casaram com a votação por candidato por diferença de grafia no nome do município e entram com zero voto no lula;
- pela lei 6.091/1974, candidatos e partidos não podem fornecer transporte a eleitores no dia da eleição.

- os arquivos de seção usados aqui não trazem votação por candidato, então os pontos dos locais de votação mostram abstenção ou tipo de área, não votos no lula;
- zonas e seções não têm polígono próprio: o mapa colore municípios e posiciona seções no ponto do seu local de votação;
- 1.606 seções (0,3%) não têm coordenada válida no tse e aparecem só nas listas;
- 594 locais (0,6%) caem fora de qualquer setor censitário mesmo com 300 m de tolerância;
- 7 municípios criados após a malha municipal usada entram nos totais mas não aparecem no mapa;
- o tipo de área descreve onde a pessoa **vota**, que costuma ser perto, mas não necessariamente no setor onde mora;
- o ibge não tem categoria "periferia". favela e comunidade urbana e urbana de baixa densidade são o mais próximo disso.

## scripts

`scripts/` tem o processamento em python (pandas + geopandas), na ordem `prep.py` → `secao.py` → `area.py` → `lula.py` → `vitoria.py` → `secao_lula.py` → `prioridade.py` → `remoto.py` → `regiao.py`. eles recebem como argumento a pasta de trabalho com os arquivos brutos do tse e do ibge, e os caminhos dos gpkg de setores em `area.py` precisam ser ajustados pro seu ambiente.
