# abstenção nas eleições gerais de 2026 (1º turno)

mapa interativo da abstenção no 1º turno de 4/10/2026, com três níveis de leitura:

- **município**: choropleth do brasil inteiro;
- **local de votação**: pontos por estado, com a abstenção de cada seção;
- **tipo de área**: setor censitário do censo 2022 em que cada local de votação cai.

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
| abstenção por seção | tse, `detalhe_votacao_secao_2026` (arquivo `_BR`, cargo presidente) |
| coordenadas dos locais | tse, `eleitorado_local_votacao_2026` (1º turno) |
| malha municipal | ibge, via [geodata-br](https://github.com/tbrugz/geodata-br) |
| códigos tse → ibge | [betafcc/Municipios-Brasileiros-TSE](https://github.com/betafcc/Municipios-Brasileiros-TSE) |
| tipo de área | ibge, malha de setores censitários do censo 2022 (`CD_SIT`, `CD_TIPO`, `NM_BAIRRO`) |

abstenção = abstenções ÷ eleitores aptos.

### arquivos em `data/`

um json por uf com a lista de locais de votação. cada item é:

`[lat, lon, nome_local, municipio, zona, bairro, [[secao, aptos, abstencoes], ...], tipo_area]`

códigos de `tipo_area`: 0 centro · 1 favela e comunidade urbana · 2 urbana alta densidade · 3 urbana baixa densidade · 4 núcleo urbano · 5 rural aglomerado · 6 rural área dispersa · 7 indígena ou quilombola · 8 outro · `null` sem setor.

## limitações

- zonas e seções não têm polígono próprio: o mapa colore municípios e posiciona seções no ponto do seu local de votação;
- 1.606 seções (0,3%) não têm coordenada válida no tse e aparecem só nas listas;
- 594 locais (0,6%) caem fora de qualquer setor censitário mesmo com 300 m de tolerância;
- 7 municípios criados após a malha municipal usada entram nos totais mas não aparecem no mapa;
- o tipo de área descreve onde a pessoa **vota**, que costuma ser perto, mas não necessariamente no setor onde mora;
- o ibge não tem categoria "periferia". favela e comunidade urbana e urbana de baixa densidade são o mais próximo disso.

## scripts

`scripts/` tem o processamento em python (pandas + geopandas), na ordem `prep.py` → `secao.py` → `area.py`. eles recebem como argumento a pasta de trabalho com os arquivos brutos do tse e do ibge, e os caminhos dos gpkg de setores em `area.py` precisam ser ajustados pro seu ambiente.
